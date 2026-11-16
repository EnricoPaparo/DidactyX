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
    @Published var workspaceSection = "brief"
    @Published var planning: PlanningState?
    @Published var displayedPlan: PlanVersion?
    @Published var showRegeneration = false
    @Published var startingPlanning = false
    @Published var exporting = false
    @Published var exportedPDF: String?
    @Published var lessonState: LessonState?
    @Published var displayedLesson: LessonVersion?
    @Published var lessonHTML = ""
    @Published var lessonBrief = "" { didSet { scheduleLessonSave() } }
    @Published var selectedLessonId: String?
    @Published var selectedLessonPlanId: String?
    @Published var startingLesson = false
    @Published var exportingLesson = false
    @Published var exportedLessonPDF: String?
    var lessonPoll: Task<Void, Never>?
    var lessonSaveTask: Task<Void, Never>?
    var selectingLesson = false
    var savingLessonBrief = false
    var savedLessonBrief = ""
    private var planningPoll: Task<Void, Never>?
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
            await refreshPlanning()
        } catch { errorMessage = error.localizedDescription }
    }

    func open(_ program: Program) async {
        guard await flush() else { return }
        setSelection(program)
        await refreshPlanning()
        if planning?.currentPlan != nil || planning?.latestJob?.isRunning == true { workspaceSection = "plan" }
    }

    private func setSelection(_ program: Program) {
        selecting = true
        selected = program
        planningPoll?.cancel()
        clearLesson()
        planning = nil
        displayedPlan = nil
        exportedPDF = nil
        workspaceSection = "brief"
        savedDraft = ProgramDraft(program)
        draft = savedDraft
        saveLabel = "Salvato"
        selecting = false
    }

    func goHome() async {
        guard await flush() else { return }
        selecting = true
        selected = nil
        planningPoll?.cancel()
        clearLesson()
        planning = nil
        displayedPlan = nil
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
                errorMessage = nil
                if let currentPlan = planning?.currentPlan { planning?.briefPending = snapshot.brief != currentPlan.brief }
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
        lessonSaveTask?.cancel()
        while savingLessonBrief { try? await Task.sleep(for: .milliseconds(20)) }
        guard await saveLessonBrief() else { return false }
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

    func refreshPlanning() async {
        guard let id = selected?.id else { return }
        do {
            let state = try decode(PlanningState.self, from: await engine.request("plan.state", ["program_id": .string(id)]))
            guard selected?.id == id else { return }
            let previousHead = planning?.currentPlan?.id
            let viewingHistory = displayedPlan != nil && displayedPlan?.id != previousHead
            planning = state
            if !viewingHistory {
                if displayedPlan?.id != state.currentPlan?.id { exportedPDF = nil }
                displayedPlan = state.currentPlan
            }
            if displayedPlan == nil, let first = state.versions.first { await showPlanVersion(first.id) }
            if state.latestJob?.isRunning == true { pollPlanning() }
        } catch { if selected?.id == id { errorMessage = error.localizedDescription } }
    }

    func startPlanning(changeRequest: String = "", review: Bool = false) async {
        guard !startingPlanning, let id = selected?.id else { return }
        startingPlanning = true
        defer { startingPlanning = false }
        guard await flush() else { return }
        do {
            let method = review ? "plan.review" : "plan.generate"
            _ = try await engine.request(method, ["program_id": .string(id), "change_request": .string(changeRequest)])
            guard selected?.id == id else { return }
            errorMessage = nil
            showRegeneration = false
            workspaceSection = "plan"
            exportedPDF = nil
            displayedPlan = planning?.currentPlan
            await refreshPlanning()
        } catch { errorMessage = error.localizedDescription }
    }

    private func pollPlanning() {
        planningPoll?.cancel()
        guard let jobId = planning?.latestJob?.id, let programId = selected?.id else { return }
        planningPoll = Task {
            while !Task.isCancelled, selected?.id == programId {
                do {
                    try await Task.sleep(for: .milliseconds(1200))
                    let job = try decode(PlanningJob.self, from: await engine.request("job.get", ["id": .string(jobId)]))
                    guard !Task.isCancelled, selected?.id == programId else { return }
                    planning?.latestJob = job
                    if !job.isRunning { await refreshPlanning(); return }
                } catch is CancellationError { return }
                catch { errorMessage = error.localizedDescription; return }
            }
        }
    }

    func cancelPlanning() async {
        guard let job = planning?.latestJob else { return }
        do {
            _ = try await engine.request("job.cancel", ["id": .string(job.id)])
            await refreshPlanning()
            if selectedLessonId != nil { await refreshLesson() }
        } catch { errorMessage = error.localizedDescription }
    }

    func resumePlanning() async {
        guard let job = planning?.latestJob else { return }
        do {
            _ = try await engine.request("job.resume", ["id": .string(job.id)])
            await refreshPlanning()
            if selectedLessonId != nil { await refreshLesson() }
        } catch { errorMessage = error.localizedDescription }
    }

    func showPlanVersion(_ id: String) async {
        guard let programId = selected?.id else { return }
        do {
            let value = try decode(PlanVersion.self, from: await engine.request("plan.version", ["program_id": .string(programId), "plan_id": .string(id)]))
            guard selected?.id == programId else { return }
            displayedPlan = value
            exportedPDF = nil
        } catch { errorMessage = error.localizedDescription }
    }

    func exportPlan() async {
        guard !exporting, let id = selected?.id, let version = displayedPlan else { return }
        exporting = true
        defer { exporting = false }
        guard await flush() else { return }
        do {
            let result = try await engine.request("plan.export", ["program_id": .string(id), "plan_id": .string(version.id)], timeout: 60)
            guard selected?.id == id, displayedPlan?.id == version.id else { return }
            exportedPDF = result["path"]?.string
            errorMessage = nil
        } catch { errorMessage = error.localizedDescription }
    }

    func applyReviewSuggestions() async {
        guard let report = planning?.latestReview?.data else { return }
        let suggestions = report["findings"]?.items.map {
            "\($0.text("location")): \($0.text("description")) Proposta: \($0.text("suggestion"))"
        }.joined(separator: "\n") ?? ""
        await startPlanning(changeRequest: "Rielabora l'intero scheletro considerando questa revisione e mantenendo i vincoli espliciti del docente.\n" + suggestions)
    }
}
