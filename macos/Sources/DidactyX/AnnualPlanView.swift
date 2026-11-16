import AppKit
import SwiftUI

func hourText(_ value: JSONValue?) -> String {
    guard let number = value?.number else { return "0" }
    return number.formatted(.number.precision(.fractionLength(0...2)).locale(Locale(identifier: "it_IT")))
}

struct PlanField: View {
    let label: String
    let values: [String]
    var body: some View {
        if !values.isEmpty {
            VStack(alignment: .leading, spacing: 6) {
                FieldLabel(text: label)
                ForEach(Array(values.enumerated()), id: \.offset) { _, value in
                    HStack(alignment: .firstTextBaseline, spacing: 7) {
                        if values.count > 1 { Text("•").foregroundStyle(Theme.secondary) }
                        Text(value).textSelection(.enabled)
                    }.font(.system(size: 13)).lineSpacing(4)
                }
            }
        }
    }
}

struct AnnualPlanView: View {
    @EnvironmentObject var model: AppModel
    private var running: Bool { model.planning?.latestJob?.isRunning == true }
    private var historical: Bool { model.displayedPlan?.id != model.planning?.currentPlan?.id }
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 25) {
                header
                if let job = model.planning?.latestJob { PlanningStatusView(job: job) }
                if let version = model.displayedPlan {
                    if version.brief != model.draft.brief {
                        Label("Il brief è cambiato. Questa versione conserva il contesto da cui è stata generata.", systemImage: "info.circle")
                            .font(.system(size: 12)).foregroundStyle(Theme.warning)
                    }
                    if historical {
                        Text("Versione precedente o non applicata al brief corrente.").font(Theme.mono(11)).foregroundStyle(Theme.secondary)
                    }
                    context(version.data["context"] ?? .null)
                    ForEach(Array((version.data["udas"]?.items ?? []).enumerated()), id: \.offset) { index, uda in
                        UdaCard(value: uda, number: index + 1, plan: version.data)
                    }
                    projects(version.data["projects"]?.items ?? [])
                    let notes = version.data["review_notes"]?.strings ?? []
                    if !notes.isEmpty {
                        DisclosureGroup("Note della revisione generativa") { PlanField(label: "Osservazioni", values: notes).padding(.top, 14) }
                            .font(.system(size: 13)).tint(Theme.cyan)
                    }
                    if let review = model.planning?.latestReview, review.planId == version.id {
                        ReviewPanel(report: review.data, disabled: running || historical)
                    }
                } else if !running {
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Il percorso prende forma dal brief.").font(.system(size: 22, weight: .medium))
                        Text("Le UDA, le lezioni e le ore verranno progettate e revisionate insieme, considerando l’intero anno.")
                            .font(.system(size: 14)).foregroundStyle(Theme.secondary).lineSpacing(5)
                        Button("Genera percorso annuale") { Task { await model.startPlanning() } }
                            .buttonStyle(PrimaryButton()).disabled(model.startingPlanning)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading).padding(26)
                    .background(Theme.panel, in: RoundedRectangle(cornerRadius: 12))
                }
                if let path = model.exportedPDF {
                    HStack {
                        Label("PDF salvato", systemImage: "checkmark.circle").foregroundStyle(Theme.cyan)
                        Spacer()
                        Button("Apri PDF") { NSWorkspace.shared.open(URL(fileURLWithPath: path)) }.buttonStyle(QuietButton())
                    }.font(.system(size: 12))
                }
            }
            .padding(32).frame(maxWidth: 960, alignment: .leading).frame(maxWidth: .infinity, alignment: .topLeading)
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 17) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 9) {
                    FieldLabel(text: "Progettazione didattica")
                    Text("Percorso annuale").font(.system(size: 29, weight: .medium)).tracking(-0.7)
                }
                Spacer()
                if let versions = model.planning?.versions, !versions.isEmpty {
                    Menu {
                        ForEach(versions) { version in
                            Button("Versione \(version.version)\(version.id == model.planning?.currentPlan?.id ? " · corrente" : "")") {
                                Task { await model.showPlanVersion(version.id) }
                            }
                        }
                    } label: {
                        Text("Versione \(model.displayedPlan?.version ?? versions.first?.version ?? 1)").font(Theme.mono(11))
                    }.menuStyle(.borderlessButton).frame(width: 115)
                }
            }
            if model.displayedPlan != nil {
                HStack(spacing: 10) {
                    Button("Rigenera scheletro") { model.showRegeneration = true }.buttonStyle(PrimaryButton()).disabled(running || model.startingPlanning)
                    Button("Revisiona") { Task { await model.startPlanning(review: true) } }.buttonStyle(QuietButton()).disabled(running || historical || model.startingPlanning)
                    Spacer()
                    Button(model.exporting ? "Esportazione…" : "Esporta PDF") { Task { await model.exportPlan() } }
                        .buttonStyle(QuietButton()).disabled(model.exporting)
                }
            }
        }
    }

    private func context(_ value: JSONValue) -> some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack(alignment: .firstTextBaseline) {
                Text(value.text("subject")).font(.system(size: 20, weight: .medium))
                Spacer()
                Text(hourText(value["total_hours"]) + " ore").font(Theme.mono(15, .medium)).foregroundStyle(Theme.cyan)
            }
            let hours = value["hours"] ?? .null
            Text("Teoria \(hourText(hours["theory"])) h · Laboratorio \(hourText(hours["laboratory"])) h · Verifiche \(hourText(hours["assessment"])) h")
                .font(Theme.mono(10)).foregroundStyle(Theme.secondary)
            Text("Riserva recupero \(hourText(hours["recovery"])) h · Margine \(hourText(hours["buffer"])) h")
                .font(Theme.mono(10)).foregroundStyle(Theme.secondary)
            PlanField(label: "Obiettivi annuali", values: value["goals"]?.items.map { $0.text("description") } ?? [])
            DisclosureGroup("Contesto e ipotesi di progettazione") {
                VStack(alignment: .leading, spacing: 17) {
                    PlanField(label: "Scuola", values: [value.text("school_context")])
                    PlanField(label: "Classe", values: [value.text("class_profile")])
                    PlanField(label: "Conoscenze iniziali", values: value["starting_knowledge"]?.strings ?? [])
                    PlanField(label: "Ipotesi", values: value["assumptions"]?.strings ?? [])
                    PlanField(label: "Indicazioni", values: value["preferences"]?.strings ?? [])
                    PlanField(label: "Argomenti essenziali", values: value["required_topics"]?.strings ?? [])
                    PlanField(label: "Argomenti facoltativi", values: value["optional_topics"]?.strings ?? [])
                    PlanField(label: "Riferimenti forniti", values: value["curriculum_references"]?.strings ?? [])
                }.padding(.top, 16)
            }.font(.system(size: 12)).tint(Theme.cyan)
        }
        .padding(23).background(Theme.panel, in: RoundedRectangle(cornerRadius: 11))
        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.border))
    }

    @ViewBuilder
    private func projects(_ values: [JSONValue]) -> some View {
        if !values.isEmpty {
            Text("Progetti progressivi").font(.system(size: 21, weight: .medium))
            ForEach(Array(values.enumerated()), id: \.offset) { _, value in
                VStack(alignment: .leading, spacing: 14) {
                    Text(value.text("title")).font(.system(size: 16, weight: .medium))
                    Text(value.text("description")).font(.system(size: 13)).foregroundStyle(Theme.secondary).lineSpacing(4)
                    PlanField(label: "Competenze", values: value["competences"]?.strings ?? [])
                    ForEach(Array((value["milestones"]?.items ?? []).enumerated()), id: \.offset) { _, item in
                        PlanField(label: udaTitle(item.text("uda_id")), values: [item.text("description"), "Risultato: " + item.text("deliverable")])
                    }
                }.padding(23).frame(maxWidth: .infinity, alignment: .leading)
                    .background(Theme.panel, in: RoundedRectangle(cornerRadius: 11))
            }
        }
    }

    private func udaTitle(_ id: String) -> String {
        model.displayedPlan?.data["udas"]?.items.first(where: { $0.text("id") == id })?.text("title") ?? id
    }
}

struct PlanningStatusView: View {
    @EnvironmentObject var model: AppModel
    let job: PlanningJob
    var body: some View {
        HStack(alignment: .center, spacing: 13) {
            if job.isRunning { ProgressView().controlSize(.small) }
            else { Image(systemName: job.status == "completed" ? "checkmark.circle" : "pause.circle").foregroundStyle(Theme.cyan) }
            Text(job.message).font(.system(size: 12)).lineSpacing(3)
            Spacer()
            if job.isRunning {
                Button("Interrompi") { Task { await model.cancelPlanning() } }.buttonStyle(QuietButton())
            } else if job.canResume {
                Button("Riprendi") { Task { await model.resumePlanning() } }.buttonStyle(QuietButton())
            }
        }
        .padding(16).background(Theme.cyan.opacity(0.045), in: RoundedRectangle(cornerRadius: 9))
    }
}

struct UdaCard: View {
    let value: JSONValue
    let number: Int
    let plan: JSONValue
    @State private var expanded = false
    var body: some View {
        DisclosureGroup(isExpanded: $expanded) {
            VStack(alignment: .leading, spacing: 19) {
                Text(value.text("description")).font(.system(size: 14)).lineSpacing(4)
                PlanField(label: "Periodo", values: [value.text("period")])
                PlanField(label: "Prerequisiti", values: value["prerequisites"]?.strings ?? [])
                PlanField(label: "Obiettivi annuali collegati", values: (value["annual_goal_ids"]?.strings ?? []).compactMap { id in
                    plan["context"]?["goals"]?.items.first(where: { $0.text("id") == id })?.text("description")
                })
                PlanField(label: "Obiettivi", values: value["objectives"]?.items.map { $0.text("description") } ?? [])
                PlanField(label: "Conoscenze", values: value["knowledge"]?.strings ?? [])
                PlanField(label: "Abilità", values: value["skills"]?.strings ?? [])
                PlanField(label: "Competenze", values: value["competences"]?.strings ?? [])
                PlanField(label: "Concetti", values: value["topics"]?.strings ?? [])
                PlanField(label: "Concetti facoltativi", values: value["optional_topics"]?.strings ?? [])
                PlanField(label: "Metodologie", values: value["methods"]?.strings ?? [])
                PlanField(label: "Valutazione", values: value["assessment"]?.strings ?? [])
                Text("Lezioni previste").font(.system(size: 16, weight: .medium)).padding(.top, 6)
                ForEach(Array((value["lessons"]?.items ?? []).enumerated()), id: \.offset) { index, lesson in
                    LessonMetadata(value: lesson, number: index + 1, uda: value, plan: plan)
                }
            }.padding(.top, 21)
        } label: {
            VStack(alignment: .leading, spacing: 10) {
                FieldLabel(text: "UDA \(number) · \(value["lessons"]?.items.count ?? 0) lezioni")
                Text(value.text("title")).font(.system(size: 20, weight: .medium))
                let hours = value["hours"] ?? .null
                Text("Teoria \(hourText(hours["theory"])) h · Laboratorio \(hourText(hours["laboratory"])) h · Verifiche \(hourText(hours["assessment"])) h")
                    .font(Theme.mono(10)).foregroundStyle(Theme.secondary)
            }
        }
        .tint(Theme.cyan).padding(23).background(Theme.panel, in: RoundedRectangle(cornerRadius: 11))
        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.border))
    }
}

struct LessonMetadata: View {
    let value: JSONValue
    let number: Int
    let uda: JSONValue
    let plan: JSONValue
    private var kind: String { ["theory": "Teoria", "laboratory": "Laboratorio", "assessment": "Verifica"][value.text("kind")] ?? "Lezione" }
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .firstTextBaseline) {
                Text("\(number). \(value.text("title"))").font(.system(size: 14, weight: .medium))
                Spacer()
                Text("\(value.text("id")) · \(kind) · \(hourText(value["duration_hours"])) h").font(Theme.mono(9)).foregroundStyle(Theme.cyan)
            }
            Text(value.text("description")).font(.system(size: 12)).foregroundStyle(Theme.secondary).lineSpacing(4)
            PlanField(label: "Obiettivi", values: (value["objective_ids"]?.strings ?? []).compactMap { id in uda["objectives"]?.items.first(where: { $0.text("id") == id })?.text("description") })
            PlanField(label: "Concetti", values: value["concepts"]?.strings ?? [])
            PlanField(label: "Lezioni propedeutiche", values: (value["prerequisite_lesson_ids"]?.strings ?? []).compactMap { id in
                plan["udas"]?.items.flatMap { $0["lessons"]?.items ?? [] }.first(where: { $0.text("id") == id })?.text("title")
            })
            PlanField(label: "Metodologie", values: value["methods"]?.strings ?? [])
            PlanField(label: "Progetti", values: (value["project_ids"]?.strings ?? []).compactMap { id in plan["projects"]?.items.first(where: { $0.text("id") == id })?.text("title") })
        }
        .padding(17).background(Theme.background.opacity(0.6), in: RoundedRectangle(cornerRadius: 8))
    }
}

struct ReviewPanel: View {
    @EnvironmentObject var model: AppModel
    let report: JSONValue
    let disabled: Bool
    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text("Revisione del percorso").font(.system(size: 20, weight: .medium))
            Text(report.text("summary")).font(.system(size: 13)).lineSpacing(4)
            ForEach(Array((report["findings"]?.items ?? []).enumerated()), id: \.offset) { _, item in
                VStack(alignment: .leading, spacing: 7) {
                    FieldLabel(text: ["error": "Correttezza", "coherence": "Coerenza", "didactic": "Indicazione didattica"][item.text("kind")] ?? "Osservazione")
                    Text(item.text("location")).font(.system(size: 13, weight: .medium))
                    Text(item.text("description")).font(.system(size: 12)).foregroundStyle(Theme.secondary)
                    Text(item.text("suggestion")).font(.system(size: 12)).lineSpacing(4)
                }
            }
            if !(report["findings"]?.items.isEmpty ?? true) {
                Button("Rigenera con questi suggerimenti") { Task { await model.applyReviewSuggestions() } }
                    .buttonStyle(QuietButton()).disabled(disabled || model.startingPlanning)
            }
            Text("Puoi mantenere il percorso così com’è. Gli aggiustamenti passano dalla rigenerazione dell’intero scheletro.")
                .font(.system(size: 11)).foregroundStyle(Theme.secondary)
        }.padding(23).background(Theme.panel, in: RoundedRectangle(cornerRadius: 11))
    }
}

struct RegenerationPanel: View {
    @EnvironmentObject var model: AppModel
    @Environment(\.dismiss) var dismiss
    @State private var request = ""
    var body: some View {
        VStack(alignment: .leading, spacing: 23) {
            HStack {
                Text("Rigenera lo scheletro").font(.system(size: 24, weight: .medium))
                Spacer()
                Button { dismiss() } label: { Image(systemName: "xmark") }.buttonStyle(.plain).accessibilityLabel("Chiudi rigenerazione")
            }
            Text("Il motore ricostruirà e revisionerà l’intero percorso usando il brief attuale. La versione precedente rimarrà disponibile.")
                .font(.system(size: 14)).foregroundStyle(Theme.secondary).lineSpacing(5)
            FieldLabel(text: "Richiesta di modifica · facoltativa")
            TextEditor(text: $request).font(.system(size: 14)).scrollContentBackground(.hidden)
                .padding(12).frame(height: 160).background(Theme.panel, in: RoundedRectangle(cornerRadius: 8))
                .overlay(RoundedRectangle(cornerRadius: 8).stroke(Theme.border))
                .accessibilityLabel("Richiesta di modifica del percorso")
            HStack {
                Text("Puoi anche usare soltanto il brief aggiornato.").font(.system(size: 12)).foregroundStyle(Theme.secondary)
                Spacer()
                Button("Rigenera tutto") { Task { await model.startPlanning(changeRequest: request) } }
                    .buttonStyle(PrimaryButton()).disabled(model.startingPlanning)
            }
        }
        .padding(30).frame(width: 670).background(Theme.background).foregroundStyle(Theme.text).preferredColorScheme(.dark)
        .interactiveDismissDisabled(model.startingPlanning)
    }
}
