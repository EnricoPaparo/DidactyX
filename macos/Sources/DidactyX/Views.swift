import AppKit
import SwiftUI

struct RootView: View {
    @EnvironmentObject var model: AppModel
    var body: some View {
        VStack(spacing: 0) {
            if let error = model.errorMessage {
                HStack(spacing: 12) {
                    Image(systemName: "exclamationmark.circle")
                    Text(error).font(.system(size: 12))
                    Spacer()
                    if !model.ready { Button("Riprova") { Task { await model.start() } }.buttonStyle(.plain) }
                    Button { model.errorMessage = nil } label: { Image(systemName: "xmark") }
                        .buttonStyle(.plain).accessibilityLabel("Chiudi messaggio")
                }
                .foregroundStyle(Theme.warning).padding(14)
                .background(Theme.warning.opacity(0.08))
            }
            if model.selected != nil { WorkspaceView() }
            else { LibraryView() }
        }
        .frame(minWidth: 940, minHeight: 660)
        .background(Theme.background)
        .foregroundStyle(Theme.text)
        .preferredColorScheme(.dark)
        .sheet(isPresented: $model.showNewProgram) { NewProgramView().environmentObject(model) }
        .sheet(isPresented: $model.showSettings) { SettingsPanel().environmentObject(model) }
        .sheet(isPresented: $model.showRegeneration) { RegenerationPanel().environmentObject(model) }
        .task { await model.start() }
    }
}

struct LibraryView: View {
    @EnvironmentObject var model: AppModel
    private let columns = [GridItem(.adaptive(minimum: 270, maximum: 420), spacing: 18, alignment: .top)]
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack {
                Brand()
                Spacer()
                Button { model.showSettings = true } label: { Image(systemName: "gearshape").frame(width: 18, height: 18) }
                    .buttonStyle(QuietButton()).help("Impostazioni").accessibilityLabel("Impostazioni")
                Button { model.showNewProgram = true } label: { Label("Nuovo programma", systemImage: "plus") }
                    .buttonStyle(PrimaryButton()).disabled(!model.ready)
            }
            .padding(.top, 40).padding(.bottom, 45)
            HStack(alignment: .firstTextBaseline) {
                Text("Programmi annuali").font(.system(size: 28, weight: .medium)).tracking(-0.6)
                Spacer()
                Text(String(format: "%02d", model.programs.count)).font(Theme.mono(13)).foregroundStyle(Theme.secondary)
            }
            .padding(.bottom, 10)
            Text("Apri un programma o creane uno nuovo.")
                .font(.system(size: 14)).foregroundStyle(Theme.secondary).padding(.bottom, 28)
            if !model.ready {
                Spacer()
                HStack { Spacer(); ProgressView().controlSize(.small); Text("Apertura dell’archivio…").font(Theme.mono(12)); Spacer() }
                Spacer()
            } else if model.programs.isEmpty {
                VStack(spacing: 18) {
                    Image(systemName: "square.stack.3d.up").font(.system(size: 36, weight: .ultraLight)).foregroundStyle(Theme.cyan)
                    Text("Il tuo primo programma").font(.system(size: 23, weight: .medium))
                    Text("Raccogli il contesto della classe e gli obiettivi\nda cui prenderà forma il percorso annuale.")
                        .font(.system(size: 14)).foregroundStyle(Theme.secondary).multilineTextAlignment(.center).lineSpacing(5)
                    Button("Crea programma") { model.showNewProgram = true }.buttonStyle(PrimaryButton()).padding(.top, 8)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Theme.panel.opacity(0.45), in: RoundedRectangle(cornerRadius: 14))
                .overlay(RoundedRectangle(cornerRadius: 14).stroke(Theme.border.opacity(0.7)))
                .padding(.bottom, 30)
            } else {
                ScrollView {
                    LazyVGrid(columns: columns, alignment: .leading, spacing: 18) {
                        ForEach(model.programs) { program in
                            ProgramCard(program: program) { Task { await model.open(program) } }
                        }
                    }.padding(.bottom, 24)
                }
            }
            HStack(spacing: 7) {
                Circle().fill(model.ready ? Theme.cyan : Theme.secondary).frame(width: 5, height: 5)
                Text(model.ready ? "Archivio locale" : "Archivio in apertura").font(Theme.mono(10))
                Spacer()
                Text("Su questo Mac").font(Theme.mono(10))
            }
            .foregroundStyle(Theme.secondary).padding(.vertical, 18)
            .overlay(alignment: .top) { Rectangle().fill(Theme.border).frame(height: 1) }
        }
        .padding(.horizontal, 42)
    }
}

struct ProgramCard: View {
    let program: Program
    let action: () -> Void
    @State private var hovering = false
    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 15) {
                HStack {
                    Text(program.classLabel.isEmpty ? "CLASSE DA DEFINIRE" : program.classLabel.uppercased())
                        .font(Theme.mono(10, .medium)).tracking(1).foregroundStyle(Theme.cyan)
                    Spacer()
                    Image(systemName: "arrow.up.right").font(.system(size: 11)).foregroundStyle(Theme.secondary)
                }
                Text(program.title).font(.system(size: 20, weight: .medium)).lineLimit(2).multilineTextAlignment(.leading)
                Text(program.description.isEmpty ? "Nessuna descrizione" : program.description)
                    .font(.system(size: 13)).foregroundStyle(Theme.secondary)
                    .lineLimit(3).multilineTextAlignment(.leading).frame(maxWidth: .infinity, alignment: .leading)
                Spacer(minLength: 5)
                HStack {
                    Text("BRIEF").font(Theme.mono(9)).tracking(1)
                    Spacer()
                    Text("Apri programma").font(.system(size: 11))
                }.foregroundStyle(Theme.secondary)
            }
            .padding(22).frame(maxWidth: .infinity, minHeight: 208, alignment: .topLeading)
            .background(hovering ? Theme.raised : Theme.panel, in: RoundedRectangle(cornerRadius: 12))
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(hovering ? Theme.cyan.opacity(0.55) : Theme.border))
            .contentShape(RoundedRectangle(cornerRadius: 12))
        }
        .buttonStyle(.plain)
        .onHover { hovering = $0 }
        .animation(.easeOut(duration: 0.12), value: hovering)
        .accessibilityLabel("Apri \(program.title), \(program.classLabel)")
    }
}

struct NewProgramView: View {
    @EnvironmentObject var model: AppModel
    @Environment(\.dismiss) var dismiss
    @State private var draft = ProgramDraft()
    @FocusState private var titleFocused: Bool
    var body: some View {
        VStack(alignment: .leading, spacing: 22) {
            HStack {
                FieldLabel(text: "Nuovo percorso")
                Spacer()
                Button { dismiss() } label: { Image(systemName: "xmark") }.buttonStyle(.plain).accessibilityLabel("Chiudi")
            }
            Text("Un programma per la tua classe.").font(.system(size: 25, weight: .medium)).tracking(-0.6)
            InputField(label: "Titolo del programma", placeholder: "Es. Elettronica e laboratorio", text: $draft.title).focused($titleFocused)
            InputField(label: "Classe", placeholder: "Es. 2ª A · Istituto tecnico", text: $draft.classLabel)
            InputField(label: "Descrizione", placeholder: "Una breve descrizione del percorso", text: $draft.description, multiline: true)
            InputField(label: "Brief iniziale · facoltativo", placeholder: "Da dove partiamo? Dove vuoi portare la classe?", text: $draft.brief.freeText, multiline: true)
            if let error = model.errorMessage { Text(error).font(.system(size: 12)).foregroundStyle(Theme.warning) }
            HStack {
                Text("Potrai aggiungere dettagli nel programma.").font(.system(size: 12)).foregroundStyle(Theme.secondary)
                Spacer()
                Button(model.isCreating ? "Creazione…" : "Crea programma") { Task { await model.create(draft) } }
                    .buttonStyle(PrimaryButton()).disabled(draft.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || model.isCreating)
            }.padding(.top, 4)
        }
        .padding(30).frame(width: 610)
        .background(Theme.background).foregroundStyle(Theme.text).preferredColorScheme(.dark)
        .onAppear { titleFocused = true }
        .interactiveDismissDisabled(model.isCreating)
    }
}

struct WorkspaceView: View {
    @EnvironmentObject var model: AppModel
    @State private var detailsExpanded = false
    var body: some View {
        VStack(spacing: 0) {
            HStack(spacing: 12) {
                Button { Task { await model.goHome() } } label: { Label("Tutti i programmi", systemImage: "arrow.left") }
                    .buttonStyle(.plain).font(.system(size: 12)).foregroundStyle(Theme.secondary)
                Text("/").foregroundStyle(Theme.border)
                Text(model.draft.classLabel.isEmpty ? "Programma" : model.draft.classLabel).font(Theme.mono(11)).foregroundStyle(Theme.cyan)
                Spacer()
                if model.isSaving { ProgressView().controlSize(.mini) }
                Text(model.saveLabel).font(Theme.mono(10)).foregroundStyle(model.saveLabel == "Non salvato" ? Theme.warning : Theme.secondary)
                Button { model.showSettings = true } label: { Image(systemName: "gearshape") }
                    .buttonStyle(.plain).padding(.leading, 12).accessibilityLabel("Impostazioni")
            }
            .padding(.horizontal, 28).padding(.top, 29).padding(.bottom, 22)
            Rectangle().fill(Theme.border).frame(height: 1)
            HStack(spacing: 0) {
                VStack(alignment: .leading, spacing: 22) {
                    Brand(compact: true).padding(.bottom, 14)
                    Text(model.draft.title).font(.system(size: 19, weight: .medium)).fixedSize(horizontal: false, vertical: true)
                    FieldLabel(text: "Programma").padding(.top, 8)
                    sidebarButton("Brief della classe", icon: "text.alignleft", value: "brief")
                    sidebarButton("Percorso annuale", icon: "list.bullet.rectangle", value: "plan")
                    sidebarButton("Dati del programma", icon: "square.grid.2x2", value: "details")
                    Spacer()
                    HStack(spacing: 7) {
                        Circle().fill(Theme.cyan).frame(width: 4, height: 4)
                        Text("CONTESTO DELLA CLASSE").font(Theme.mono(8)).tracking(0.7)
                    }.foregroundStyle(Theme.secondary)
                }
                .padding(24).frame(width: 230).background(Theme.panel.opacity(0.45))
                Rectangle().fill(Theme.border).frame(width: 1)
                if model.workspaceSection == "lesson" {
                    LessonWorkspace()
                } else if model.workspaceSection == "plan" {
                    AnnualPlanView()
                } else { ScrollView {
                    VStack(alignment: .leading, spacing: 24) {
                        if model.workspaceSection == "brief" {
                            VStack(alignment: .leading, spacing: 10) {
                                FieldLabel(text: "Punto di partenza")
                                Text("Brief della classe").font(.system(size: 30, weight: .medium)).tracking(-0.8)
                                Text("Scrivi liberamente: situazione iniziale, obiettivi, vincoli e qualsiasi indicazione utile.")
                                    .font(.system(size: 14)).foregroundStyle(Theme.secondary).lineSpacing(4)
                            }
                            ZStack(alignment: .topLeading) {
                                if model.draft.brief.freeText.isEmpty {
                                    Text("Racconta la tua classe e il percorso che immagini…")
                                        .font(.system(size: 15)).foregroundStyle(Theme.secondary.opacity(0.7))
                                        .padding(.horizontal, 19).padding(.vertical, 19).allowsHitTesting(false)
                                }
                                TextEditor(text: $model.draft.brief.freeText)
                                    .font(.system(size: 15)).lineSpacing(5).scrollContentBackground(.hidden)
                                    .padding(14).frame(minHeight: 270)
                                    .accessibilityLabel("Brief libero della classe")
                            }
                            .background(Theme.panel, in: RoundedRectangle(cornerRadius: 10))
                            .overlay(RoundedRectangle(cornerRadius: 10).stroke(Theme.border))
                            DisclosureGroup(isExpanded: $detailsExpanded) {
                                VStack(spacing: 20) {
                                    InputField(label: "Scuola e contesto", placeholder: "Tipo di scuola, indirizzo, materia, età…", text: $model.draft.brief.schoolContext, multiline: true)
                                    InputField(label: "Gli studenti", placeholder: "Interessi, difficoltà, ritmo, bisogni…", text: $model.draft.brief.studentProfile, multiline: true)
                                    InputField(label: "Conoscenze di partenza", placeholder: "Cosa sanno già e cosa va consolidato", text: $model.draft.brief.startingKnowledge, multiline: true)
                                    InputField(label: "Obiettivi e competenze", placeholder: "Dove vuoi portare la classe", text: $model.draft.brief.objectives, multiline: true)
                                    InputField(label: "Argomenti", placeholder: "Concetti essenziali e facoltativi", text: $model.draft.brief.topics, multiline: true)
                                    InputField(label: "Tempi e laboratorio", placeholder: "Ore, strumenti, attività e progetti", text: $model.draft.brief.organisation, multiline: true)
                                    InputField(label: "Le tue indicazioni", placeholder: "Stile, profondità e preferenze didattiche", text: $model.draft.brief.preferences, multiline: true)
                                }.padding(.top, 22)
                            } label: {
                                Text("Aggiungi dettagli · facoltativo").font(.system(size: 13, weight: .medium))
                            }.tint(Theme.cyan)
                            HStack(spacing: 8) {
                                Image(systemName: "checkmark.circle").foregroundStyle(Theme.cyan)
                                Text("Le indicazioni vengono salvate automaticamente su questo Mac.")
                                    .foregroundStyle(Theme.secondary)
                            }.font(.system(size: 12)).padding(.top, 8)
                            HStack {
                                if model.planning?.currentPlan != nil {
                                    Button("Rigenera da questo brief") { model.showRegeneration = true }.buttonStyle(PrimaryButton())
                                } else {
                                    Button("Genera percorso annuale") { Task { await model.startPlanning() } }.buttonStyle(PrimaryButton())
                                }
                                Spacer()
                            }.disabled(model.startingPlanning || model.planning?.latestJob?.isRunning == true)
                        } else {
                            Text("Dati del programma").font(.system(size: 30, weight: .medium)).tracking(-0.8)
                            Text("Le informazioni con cui riconosci questo percorso nella raccolta.").font(.system(size: 14)).foregroundStyle(Theme.secondary)
                            InputField(label: "Titolo", placeholder: "Titolo del programma", text: $model.draft.title)
                            InputField(label: "Classe", placeholder: "Classe e indirizzo", text: $model.draft.classLabel)
                            InputField(label: "Descrizione", placeholder: "Descrizione del percorso", text: $model.draft.description, multiline: true)
                        }
                    }
                    .frame(maxWidth: 740, alignment: .leading)
                    .padding(38).frame(maxWidth: .infinity, alignment: .topLeading)
                }
                }
            }
        }
    }

    private func sidebarButton(_ title: String, icon: String, value: String) -> some View {
        Button { model.workspaceSection = value } label: {
            HStack(spacing: 10) { Image(systemName: icon).frame(width: 16); Text(title); Spacer() }
                .font(.system(size: 12, weight: model.workspaceSection == value ? .medium : .regular))
                .foregroundStyle(model.workspaceSection == value ? Theme.cyan : Theme.secondary)
                .padding(11).background(model.workspaceSection == value ? Theme.cyan.opacity(0.07) : .clear, in: RoundedRectangle(cornerRadius: 7))
        }.buttonStyle(.plain)
    }
}
