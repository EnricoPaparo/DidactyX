import AppKit
import SwiftUI

@MainActor
final class AppModel: ObservableObject {
    let engine = EngineClient()
    @Published var programs: [Program] = []
    @Published var selected: Program?
    @Published var draft = ProgramDraft() {
        didSet { if !selecting { scheduleSave() } }
    }
    @Published var ready = false
    @Published var errorMessage: String?
    @Published var showNewProgram = false
    @Published var showSettings = false
    @Published var isCreating = false
    @Published var saveLabel = "Salvato"
    @Published var isSaving = false
    @Published var settings: LocalSettings?
    @Published var account: AccountStatus?
    @Published var readingAccount = false
    @Published var accountError: String?
    private var savedDraft = ProgramDraft()
    private var selecting = false
    private var saveTask: Task<Void, Never>?

    func start() async {
        do {
            let ping = try await engine.request("system.ping")
            guard ping["protocol_version"]?.integer == 1 else {
                throw EngineError(message: "L’app e il motore richiedono un aggiornamento.")
            }
            programs = try decode([Program].self, from: await engine.request("program.list"))
            settings = try decode(LocalSettings.self, from: await engine.request("settings.get"))
            ready = true
            errorMessage = nil
        } catch { errorMessage = error.localizedDescription }
    }

    func create(_ value: ProgramDraft) async {
        guard !isCreating else { return }
        isCreating = true
        defer { isCreating = false }
        guard await flush() else { return }
        do {
            let result = try await engine.request("program.create", [
                "title": .string(value.title), "class_label": .string(value.classLabel),
                "description": .string(value.description), "brief": try encode(value.brief)
            ])
            let program = try decode(Program.self, from: result)
            programs.insert(program, at: 0)
            showNewProgram = false
            setSelection(program)
        } catch { errorMessage = error.localizedDescription }
    }

    func open(_ program: Program) async {
        guard await flush() else { return }
        setSelection(program)
    }

    private func setSelection(_ program: Program) {
        selecting = true
        selected = program
        savedDraft = ProgramDraft(program)
        draft = savedDraft
        saveLabel = "Salvato"
        selecting = false
    }

    func goHome() async {
        guard await flush() else { return }
        selecting = true
        selected = nil
        selecting = false
    }

    private func scheduleSave() {
        guard selected != nil, draft != savedDraft else { return }
        saveLabel = "Modifiche da salvare"
        saveTask?.cancel()
        saveTask = Task {
            do { try await Task.sleep(for: .milliseconds(550)) }
            catch { return }
            await save()
        }
    }

    private func save() async {
        guard !isSaving, selected != nil, draft != savedDraft else { return }
        isSaving = true
        defer { isSaving = false }
        while let current = selected, draft != savedDraft {
            let snapshot = draft
            saveLabel = "Salvataggio…"
            do {
                let response = try await engine.request("program.update", [
                    "id": .string(current.id), "expected_revision": .number(Double(current.revision)),
                    "changes": .object(["title": .string(snapshot.title), "class_label": .string(snapshot.classLabel),
                                        "description": .string(snapshot.description), "brief": try encode(snapshot.brief)])
                ])
                let updated = try decode(Program.self, from: response)
                selected = updated
                savedDraft = snapshot
                if let index = programs.firstIndex(where: { $0.id == updated.id }) { programs[index] = updated }
                programs.sort { $0.updatedAt > $1.updatedAt }
                saveLabel = draft == savedDraft ? "Salvato" : "Salvataggio…"
            } catch {
                saveLabel = "Non salvato"
                errorMessage = error.localizedDescription
                return
            }
        }
    }

    @discardableResult
    func flush() async -> Bool {
        saveTask?.cancel()
        while isSaving { try? await Task.sleep(for: .milliseconds(20)) }
        await save()
        return selected == nil || draft == savedDraft
    }

    func refreshAccount() async {
        guard !readingAccount else { return }
        readingAccount = true
        accountError = nil
        defer { readingAccount = false }
        do {
            account = try decode(AccountStatus.self, from: await engine.request("account.status", ["refresh": .bool(true)], timeout: 55))
        } catch { accountError = error.localizedDescription }
    }

    func chooseExportDirectory() async {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.canCreateDirectories = true
        panel.allowsMultipleSelection = false
        panel.prompt = "Scegli cartella"
        guard await panel.begin() == .OK, let url = panel.url else { return }
        do {
            settings = try decode(LocalSettings.self, from: await engine.request("settings.update", ["export_directory": .string(url.path)]))
        } catch { errorMessage = error.localizedDescription }
    }

    func openDirectory(_ path: String) {
        do {
            try FileManager.default.createDirectory(atPath: path, withIntermediateDirectories: true)
            NSWorkspace.shared.open(URL(fileURLWithPath: path))
        } catch { errorMessage = "Non riesco ad aprire questa cartella." }
    }
}
