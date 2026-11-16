import AppKit
import SwiftUI
import WebKit

struct LessonReader: NSViewRepresentable {
    let html: String
    func makeCoordinator() -> Coordinator { Coordinator() }
    func makeNSView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = false
        let view = WKWebView(frame: .zero, configuration: configuration)
        view.navigationDelegate = context.coordinator
        return view
    }
    func updateNSView(_ view: WKWebView, context: Context) {
        guard context.coordinator.html != html else { return }
        context.coordinator.html = html
        view.loadHTMLString(html, baseURL: nil)
    }
    final class Coordinator: NSObject, WKNavigationDelegate {
        var html = ""
        func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = action.request.url else { decisionHandler(.cancel); return }
            if action.navigationType == .linkActivated, ["http", "https"].contains(url.scheme ?? "") {
                NSWorkspace.shared.open(url); decisionHandler(.cancel)
            } else { decisionHandler(["about", "data"].contains(url.scheme ?? "") ? .allow : .cancel) }
        }
    }
}

struct LessonWorkspace: View {
    @EnvironmentObject var model: AppModel
    @State private var briefExpanded = false
    @State private var notesExpanded = false
    private var running: Bool { model.lessonState?.latestJob?.isRunning == true }
    private var historical: Bool { model.displayedLesson != nil && model.displayedLesson?.id != model.lessonState?.currentVersion?.id }
    private var title: String {
        model.displayedLesson?.data.text("title") ?? metadata?.text("title") ?? "Lezione"
    }
    private var metadata: JSONValue? {
        model.displayedPlan?.data["udas"]?.items.flatMap { $0["lessons"]?.items ?? [] }.first { $0.text("id") == model.selectedLessonId }
    }
    var body: some View {
        VStack(spacing: 0) {
            VStack(alignment: .leading, spacing: 10) {
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 7) {
                        FieldLabel(text: "\(model.selectedLessonId ?? "") · Contenuto della lezione")
                        Text(title).font(.system(size: 23, weight: .medium)).fixedSize(horizontal: false, vertical: true)
                    }
                    Spacer()
                    Menu("Altra lezione") {
                        ForEach(model.displayedPlan?.data["udas"]?.items ?? [], id: \.textId) { uda in
                            ForEach(uda["lessons"]?.items ?? [], id: \.textId) { lesson in
                                Button(lesson.text("id") + " · " + lesson.text("title")) {
                                    guard let planId = model.selectedLessonPlanId else { return }
                                    Task { await model.openLesson(lesson.text("id"), planId: planId) }
                                }
                            }
                        }
                    }.frame(width: 125)
                }
                HStack(spacing: 10) {
                    Button(model.displayedLesson == nil ? "Genera contenuto" : "Rigenera lezione") { Task { await model.generateLesson() } }
                        .buttonStyle(PrimaryButton()).disabled(running || historical || model.startingLesson || model.lessonState == nil || model.lessonState?.historicalPlan == true)
                    if model.displayedLesson != nil {
                        Button("Revisiona") { Task { await model.generateLesson(review: true) } }.buttonStyle(QuietButton())
                            .disabled(running || model.startingLesson || historical)
                        Spacer()
                        Button(model.exportingLesson ? "Esportazione…" : "Esporta PDF") { Task { await model.exportLesson() } }
                            .buttonStyle(QuietButton()).disabled(model.exportingLesson)
                    }
                }
                if let versions = model.lessonState?.versions, !versions.isEmpty {
                    HStack {
                        Menu("Contenuto · versione \(model.displayedLesson?.version ?? 1)") {
                            ForEach(versions) { v in Button("Versione \(v.version)") { Task { await model.showLessonVersion(v.id) } } }
                        }.menuStyle(.borderlessButton).frame(width: 180)
                        if historical { Text("Versione precedente").foregroundStyle(Theme.warning) }
                        Spacer()
                        Text("Materiale generato").foregroundStyle(Theme.secondary)
                    }.font(.system(size: 10))
                }
                DisclosureGroup(isExpanded: $briefExpanded) {
                    TextField("Indicazioni specifiche, tono, esempi o approfondimenti…", text: $model.lessonBrief, axis: .vertical)
                        .lineLimit(2...5).textFieldStyle(.plain).font(.system(size: 13)).padding(12)
                        .background(Theme.panel, in: RoundedRectangle(cornerRadius: 7)).padding(.top, 10)
                        .accessibilityLabel("Brief facoltativo della lezione").disabled(model.lessonState == nil)
                } label: { Text("Brief della lezione · facoltativo").font(.system(size: 12)) }.tint(Theme.cyan)
                if let job = model.lessonState?.latestJob, job.kind.hasPrefix("lesson_"), job.isRunning || job.canResume { PlanningStatusView(job: job) }
                if model.lessonState?.briefPending == true {
                    Text("Il brief della classe è cambiato: questa lezione usa il contesto applicato al percorso. Per applicare le nuove indicazioni, rigenera lo scheletro.")
                        .font(.system(size: 11)).foregroundStyle(Theme.warning)
                }
                if let version = model.displayedLesson, model.lessonBrief != version.brief {
                    Text("Le indicazioni specifiche sono cambiate. Rigenera la lezione per applicarle al contenuto.")
                        .font(.system(size: 11)).foregroundStyle(Theme.warning)
                }
                if !historical, let reasons = model.lessonState?.staleReasons, !reasons.isEmpty {
                    Text(reasons.joined(separator: " ") + " Revisiona o rigenera la lezione per valutarne il riallineamento.")
                        .font(.system(size: 12)).foregroundStyle(Theme.warning)
                }
                if model.displayedLesson != nil {
                    DisclosureGroup(isExpanded: $notesExpanded) {
                        ScrollView {
                            VStack(alignment: .leading, spacing: 14) {
                                PlanField(label: "Note per il docente", values: model.displayedLesson?.data["teacher_notes"]?.strings ?? [])
                                PlanField(label: "Richiami ai materiali precedenti", values: model.displayedLesson?.data["continuity"]?.items.map { ref in
                                    let code = model.displayedLesson?.context["source_versions"]?.items.first(where: { $0.text("version_id") == ref.text("version_id") })?.text("lesson_id") ?? "Lezione precedente"
                                    return code + " · " + ref.text("description")
                                } ?? [])
                                if let checks = model.displayedLesson?.checks.items, !checks.isEmpty {
                                    let passed = checks.filter { $0.text("status") == "passed" }.count
                                    Text("Esempi: \(passed) casi eseguiti con output corrispondente; \(checks.count - passed) controlli non eseguiti.").font(.system(size: 12))
                                    ForEach(Array(checks.filter { $0.text("status") != "passed" }.enumerated()), id: \.offset) { _, check in
                                        Text(check.text("message")).font(.system(size: 11)).foregroundStyle(Theme.secondary)
                                    }
                                }
                                if !historical, let review = model.lessonState?.latestReview?["data"] {
                                    Text(review.text("summary")).font(.system(size: 13))
                                    ForEach(Array((review["findings"]?.items ?? []).enumerated()), id: \.offset) { _, finding in
                                        PlanField(label: finding.text("location"), values: [finding.text("description"), finding.text("suggestion")])
                                    }
                                    if !(review["findings"]?.items.isEmpty ?? true) {
                                        Button("Rigenera con questi suggerimenti") { Task { await model.applyLessonReview() } }
                                            .buttonStyle(QuietButton()).disabled(running || model.startingLesson || model.lessonState?.historicalPlan == true)
                                    }
                                }
                            }.frame(maxWidth: .infinity, alignment: .leading).padding(.top, 12)
                        }.frame(maxHeight: 210)
                    } label: { Text("Note e revisione").font(.system(size: 12)) }.tint(Theme.cyan)
                }
                if let path = model.exportedLessonPDF {
                    HStack {
                        Label("PDF salvato", systemImage: "checkmark.circle").foregroundStyle(Theme.cyan)
                        Spacer()
                        Button("Apri PDF") { NSWorkspace.shared.open(URL(fileURLWithPath: path)) }.buttonStyle(.plain)
                    }.font(.system(size: 12))
                }
            }.padding(20)
            Rectangle().fill(Theme.border).frame(height: 1)
            if !model.lessonHTML.isEmpty { LessonReader(html: model.lessonHTML) }
            else {
                VStack(spacing: 15) {
                    Text("La spiegazione prende forma qui.").font(.system(size: 21, weight: .medium))
                    Text(metadata?.text("description") ?? "Il contenuto verrà generato nel contesto dell’intero percorso.")
                        .font(.system(size: 14)).foregroundStyle(Theme.secondary).multilineTextAlignment(.center)
                    Text("Puoi lasciare vuoto il brief: restano valide le indicazioni della classe.").font(.system(size: 12)).foregroundStyle(Theme.secondary)
                }.padding(40).frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
    }
}

extension JSONValue {
    var textId: String { text("id") }
}
