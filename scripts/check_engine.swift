import Foundation

struct CheckFailure: LocalizedError {
    let message: String
    var errorDescription: String? { message }
}

func require(_ condition: Bool, _ message: String) throws {
    if !condition { throw CheckFailure(message: message) }
}

@main
struct CheckEngine {
    static func main() async throws {
        guard let path = ProcessInfo.processInfo.environment["DIDACTYX_TEST_ENGINE"] else {
            throw CheckFailure(message: "Impostare DIDACTYX_TEST_ENGINE con il motore incluso nel pacchetto.")
        }
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: directory) }
        let executable = URL(fileURLWithPath: path)
        let first = EngineClient(executableURL: executable, dataDirectory: directory)
        do {
            let created = try decode(Program.self, from: await first.request("program.create", [
                "title": .string("Integrazione Swift e Python"),
                "brief": .object(["free_text": .string("Conoscenze iniziali e obiettivi: realtà e perché.")])
            ]))
            async let ping = first.request("system.ping")
            async let programs = first.request("program.list")
            let (pingResult, listResult) = try await (ping, programs)
            try require(pingResult["protocol_version"]?.integer == 1, "Versione del protocollo inattesa")
            try require(try decode([Program].self, from: listResult).first?.id == created.id, "Risposte concorrenti non coerenti")
            await first.stop()

            let second = EngineClient(executableURL: executable, dataDirectory: directory)
            do {
                let restored = try decode([Program].self, from: await second.request("program.list"))
                try require(restored.first == created, "I dati non sono stati conservati dopo il riavvio")
                await second.stop()
            } catch { await second.stop(); throw error }
        } catch { await first.stop(); throw error }
        print("Integrazione Swift-Python verificata: richieste concorrenti e riapertura dei dati.")
    }
}
