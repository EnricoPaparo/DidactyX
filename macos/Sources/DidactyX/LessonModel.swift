import Foundation

extension AppModel {
    func clearLesson() {
        lessonPoll?.cancel()
        selectingLesson = true
        selectedLessonId = nil; selectedLessonPlanId = nil
        lessonState = nil; displayedLesson = nil; lessonHTML = ""; lessonBrief = ""; savedLessonBrief = ""
        exportedLessonPDF = nil
        selectingLesson = false
    }

    func openLesson(_ id: String, planId: String) async {
        guard await flush() else { return }
        clearLesson()
        selectedLessonId = id; selectedLessonPlanId = planId
        workspaceSection = "lesson"
        await refreshLesson(initial: true)
    }

    func scheduleLessonSave() {
        guard !selectingLesson, selectedLessonId != nil, lessonBrief != savedLessonBrief else { return }
        lessonSaveTask?.cancel()
        lessonSaveTask = Task {
            do { try await Task.sleep(for: .milliseconds(550)) } catch { return }
            _ = await saveLessonBrief()
        }
    }

    @discardableResult
    func saveLessonBrief() async -> Bool {
        guard !savingLessonBrief else { return false }
        guard let programId = selected?.id, let planId = selectedLessonPlanId, let lessonId = selectedLessonId else { return true }
        savingLessonBrief = true
        defer { savingLessonBrief = false }
        while lessonBrief != savedLessonBrief {
            let snapshot = lessonBrief
            do {
                _ = try await engine.request("lesson.brief.save", ["program_id": .string(programId), "plan_id": .string(planId), "lesson_id": .string(lessonId), "brief": .string(snapshot)])
                savedLessonBrief = snapshot
            } catch { errorMessage = error.localizedDescription; return false }
        }
        return true
    }

    func refreshLesson(initial: Bool = false, poll: Bool = true) async {
        guard let programId = selected?.id, let planId = selectedLessonPlanId, let lessonId = selectedLessonId else { return }
        do {
            let state = try decode(LessonState.self, from: await engine.request("lesson.state", ["program_id": .string(programId), "plan_id": .string(planId), "lesson_id": .string(lessonId)]))
            guard selected?.id == programId, selectedLessonId == lessonId, selectedLessonPlanId == planId else { return }
            let history = displayedLesson != nil && displayedLesson?.id != lessonState?.currentVersion?.id
            lessonState = state
            planning?.latestJob = state.latestJob
            if initial {
                selectingLesson = true; lessonBrief = state.draftBrief; savedLessonBrief = state.draftBrief; selectingLesson = false
            }
            if !history, displayedLesson?.id != state.currentVersion?.id {
                displayedLesson = state.currentVersion; exportedLessonPDF = nil
                await loadLessonDocument()
            }
            if poll, state.latestJob?.isRunning == true { pollLesson() }
        } catch { errorMessage = error.localizedDescription }
    }

    func loadLessonDocument() async {
        guard let version = displayedLesson else { lessonHTML = ""; return }
        do {
            let result = try await engine.request("lesson.document", ["program_id": .string(version.programId), "version_id": .string(version.id)])
            guard displayedLesson?.id == version.id else { return }
            lessonHTML = result["html"]?.string ?? ""
        } catch { errorMessage = error.localizedDescription }
    }

    func showLessonVersion(_ id: String) async {
        guard let programId = selected?.id else { return }
        do {
            let version = try decode(LessonVersion.self, from: await engine.request("lesson.version", ["program_id": .string(programId), "version_id": .string(id)]))
            guard version.programId == selected?.id, version.planId == selectedLessonPlanId, version.lessonId == selectedLessonId else { return }
            displayedLesson = version; exportedLessonPDF = nil
            await loadLessonDocument()
        } catch { errorMessage = error.localizedDescription }
    }

    func generateLesson(review: Bool = false, extraBrief: String? = nil) async {
        guard !startingLesson, let programId = selected?.id, let planId = selectedLessonPlanId, let lessonId = selectedLessonId else { return }
        startingLesson = true
        defer { startingLesson = false }
        if let extraBrief { lessonBrief = extraBrief }
        guard await flush() else { return }
        do {
            _ = try await engine.request(review ? "lesson.review" : "lesson.generate", ["program_id": .string(programId), "plan_id": .string(planId), "lesson_id": .string(lessonId), "brief": .string(extraBrief ?? lessonBrief)])
            guard selected?.id == programId, selectedLessonPlanId == planId, selectedLessonId == lessonId else { return }
            displayedLesson = lessonState?.currentVersion
            await refreshPlanning(); await refreshLesson()
            errorMessage = nil
        } catch { errorMessage = error.localizedDescription }
    }

    private func pollLesson() {
        lessonPoll?.cancel()
        guard let jobId = lessonState?.latestJob?.id, let programId = selected?.id, let lessonId = selectedLessonId else { return }
        lessonPoll = Task {
            var lastPhase = ""
            while !Task.isCancelled, selected?.id == programId, selectedLessonId == lessonId {
                do {
                    try await Task.sleep(for: .milliseconds(1200))
                    let job = try decode(PlanningJob.self, from: await engine.request("job.get", ["id": .string(jobId)]))
                    guard !Task.isCancelled, selectedLessonId == lessonId, selected?.id == programId else { return }
                    lessonState?.latestJob = job; planning?.latestJob = job
                    if lastPhase != job.phase || !job.isRunning { lastPhase = job.phase; await refreshLesson(poll: false) }
                    if !job.isRunning { return }
                } catch is CancellationError { return }
                catch { errorMessage = error.localizedDescription; return }
            }
        }
    }

    func exportLesson() async {
        guard !exportingLesson, let version = displayedLesson else { return }
        exportingLesson = true
        defer { exportingLesson = false }
        do {
            let result = try await engine.request("lesson.export", ["program_id": .string(version.programId), "version_id": .string(version.id)], timeout: 60)
            guard displayedLesson?.id == version.id else { return }
            exportedLessonPDF = result["path"]?.string
        } catch { errorMessage = error.localizedDescription }
    }

    func applyLessonReview() async {
        guard let report = lessonState?.latestReview?["data"] else { return }
        let suggestions = report["findings"]?.items.map { $0.text("location") + ": " + $0.text("suggestion") }.joined(separator: "\n") ?? ""
        await generateLesson(extraBrief: lessonBrief + "\nApplica queste proposte della revisione rispettando le mie indicazioni esplicite:\n" + suggestions)
    }
}
