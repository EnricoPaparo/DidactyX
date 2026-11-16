import Foundation

actor EngineClient {
    private var process: Process?
    private var input: FileHandle?
    private var output: FileHandle?
    private var buffer = Data()
    private var pending: [String: CheckedContinuation<JSONValue, Error>] = [:]
    private var sessionID: UUID?
    private var readerTask: Task<Void, Never>?
    private let executableOverride: URL?
    private let dataDirectory: URL?

    init(executableURL: URL? = nil, dataDirectory: URL? = nil) {
        self.executableOverride = executableURL
        self.dataDirectory = dataDirectory
    }

    private func start() throws {
        if let process, process.isRunning { return }
        guard let resources = Bundle.main.resourceURL else {
            throw EngineError(message: "Non riesco a trovare i componenti dell’app.")
        }
        let executable = executableOverride ?? resources.appendingPathComponent("engine/didactyx-engine")
        guard FileManager.default.isExecutableFile(atPath: executable.path) else {
            throw EngineError(message: "Il motore locale non è disponibile. Ricostruisci l’app.")
        }
        let task = Process()
        let stdin = Pipe(), stdout = Pipe()
        task.executableURL = executable
        if let dataDirectory { task.arguments = ["--data-dir", dataDirectory.path] }
        task.standardInput = stdin
        task.standardOutput = stdout
        task.standardError = FileHandle.nullDevice
        task.environment = ProcessInfo.processInfo.environment
        let identifier = UUID()
        let stream = AsyncStream<Data> { continuation in
            stdout.fileHandleForReading.readabilityHandler = { handle in
            let data = handle.availableData
                if data.isEmpty { continuation.finish() }
                else { continuation.yield(data) }
            }
        }
        try task.run()
        sessionID = identifier
        self.process = task
        input = stdin.fileHandleForWriting
        output = stdout.fileHandleForReading
        readerTask = Task { [weak self] in
            for await data in stream { await self?.receive(data, session: identifier) }
            await self?.disconnected(session: identifier)
        }
    }

    func request(_ method: String, _ params: [String: JSONValue] = [:], timeout: Double = 15) async throws -> JSONValue {
        try start()
        let identifier = UUID().uuidString
        let envelope: JSONValue = .object(["id": .string(identifier), "method": .string(method), "params": .object(params)])
        var data = try JSONEncoder().encode(envelope)
        data.append(0x0A)
        return try await withCheckedThrowingContinuation { continuation in
            pending[identifier] = continuation
            do { try input?.write(contentsOf: data) }
            catch {
                pending.removeValue(forKey: identifier)?.resume(throwing: EngineError(message: "Il collegamento all’archivio si è interrotto."))
            }
            Task {
                try? await Task.sleep(for: .seconds(timeout))
                self.expire(identifier)
            }
        }
    }

    private func expire(_ identifier: String) {
        pending.removeValue(forKey: identifier)?.resume(throwing: EngineError(message: "L’operazione sta impiegando troppo tempo. Riprova."))
    }

    private func receive(_ data: Data, session: UUID) {
        guard sessionID == session else { return }
        if data.isEmpty { return }
        buffer.append(data)
        while let newline = buffer.firstIndex(of: 0x0A) {
            let line = buffer.prefix(upTo: newline)
            buffer.removeSubrange(...newline)
            guard let envelope = try? JSONDecoder().decode(JSONValue.self, from: Data(line)),
                  let identifier = envelope["id"]?.string,
                  let continuation = pending.removeValue(forKey: identifier) else { continue }
            if let error = envelope["error"] {
                continuation.resume(throwing: EngineError(message: error["message"]?.string ?? "L’operazione non è riuscita."))
            } else if let result = envelope["result"] {
                continuation.resume(returning: result)
            } else {
                continuation.resume(throwing: EngineError(message: "La risposta del motore non è valida."))
            }
        }
    }

    private func disconnected(session: UUID) {
        guard sessionID == session else { return }
        output?.readabilityHandler = nil
        try? output?.close()
        try? input?.close()
        sessionID = nil
        process = nil
        input = nil
        output = nil
        readerTask = nil
        buffer.removeAll()
        let waiting = pending
        pending.removeAll()
        for continuation in waiting.values {
            continuation.resume(throwing: EngineError(message: "Il collegamento all’archivio si è interrotto. Riprova."))
        }
    }

    func stop() async {
        let task = process
        try? input?.close()
        for _ in 0..<30 {
            if task?.isRunning != true { break }
            try? await Task.sleep(for: .milliseconds(50))
        }
        if task?.isRunning == true { task?.terminate() }
    }
}
