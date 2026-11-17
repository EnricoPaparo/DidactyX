import SwiftUI

struct SettingsPanel: View {
    @EnvironmentObject var model: AppModel
    @Environment(\.dismiss) var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 26) {
            HStack {
                Text("Impostazioni").font(.system(size: 25, weight: .medium)).tracking(-0.5)
                Spacer()
                Button { dismiss() } label: { Image(systemName: "xmark") }
                    .buttonStyle(.plain).accessibilityLabel("Chiudi impostazioni").keyboardShortcut(.cancelAction)
            }
            VStack(alignment: .leading, spacing: 16) {
                FieldLabel(text: "Account Codex")
                HStack(alignment: .top, spacing: 13) {
                    Image(systemName: "person.crop.circle").font(.system(size: 27, weight: .light)).foregroundStyle(Theme.cyan)
                    VStack(alignment: .leading, spacing: 7) {
                        if model.readingAccount {
                            HStack { ProgressView().controlSize(.mini); Text("Lettura dello stato…") }
                        } else {
                            Text(model.account?.connected == true ? "ChatGPT collegato" : "Stato dell’account")
                                .font(.system(size: 15, weight: .medium))
                        }
                        if let email = model.account?.email { Text(email).font(Theme.mono(11)).foregroundStyle(Theme.secondary).textSelection(.enabled) }
                        Text(model.accountError ?? model.account?.message ?? "Verifico l’accesso disponibile su questo Mac.")
                            .font(.system(size: 12)).foregroundStyle(Theme.secondary).fixedSize(horizontal: false, vertical: true)
                    }
                    Spacer()
                    if let plan = model.account?.plan {
                        Text(plan.uppercased()).font(Theme.mono(9, .medium)).tracking(1)
                            .foregroundStyle(Theme.cyan).padding(.horizontal, 9).padding(.vertical, 6)
                            .background(Theme.cyan.opacity(0.07), in: Capsule())
                    }
                }
                if let used = model.account?.usedPercent, model.account?.connected == true {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Disponibilità nella finestra corrente").font(.system(size: 11)).foregroundStyle(Theme.secondary)
                            Spacer()
                            Text("\(Int((100 - used).rounded()))%").font(Theme.mono(11)).foregroundStyle(Theme.cyan)
                        }
                        ProgressView(value: 100 - used, total: 100).tint(Theme.cyan)
                    }
                }
                HStack {
                    Text("L’accesso è gestito dal tuo client Codex.")
                        .font(.system(size: 11)).foregroundStyle(Theme.secondary)
                    Spacer()
                    Button("Rileggi stato") { Task { await model.refreshAccount() } }
                        .buttonStyle(QuietButton()).disabled(model.readingAccount)
                }
            }
            .padding(20).background(Theme.panel, in: RoundedRectangle(cornerRadius: 11))
            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.border))

            VStack(alignment: .leading, spacing: 22) {
                FieldLabel(text: "Dati locali")
                if let settings = model.settings {
                    folderRow(title: "Archivio dei programmi", path: settings.dataDirectory, canChoose: false)
                    Rectangle().fill(Theme.border).frame(height: 1)
                    folderRow(title: "Cartella dei PDF", path: settings.exportDirectory, canChoose: true)
                }
            }
            .padding(20).background(Theme.panel, in: RoundedRectangle(cornerRadius: 11))
            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.border))

            HStack {
                Text("DidactyX 0.3.2").font(Theme.mono(10))
                Spacer()
                if let version = model.account?.version { Text(version).font(Theme.mono(9)) }
            }.foregroundStyle(Theme.secondary)
        }
        .padding(30).frame(width: 620)
        .background(Theme.background).foregroundStyle(Theme.text).preferredColorScheme(.dark)
        .task { await model.refreshAccount() }
    }

    private func folderRow(title: String, path: String, canChoose: Bool) -> some View {
        HStack(alignment: .center, spacing: 12) {
            Image(systemName: "folder").foregroundStyle(Theme.secondary)
            VStack(alignment: .leading, spacing: 6) {
                Text(title).font(.system(size: 13, weight: .medium))
                Text((path as NSString).abbreviatingWithTildeInPath).font(Theme.mono(10))
                    .foregroundStyle(Theme.secondary).lineLimit(2).textSelection(.enabled)
            }
            Spacer()
            if canChoose {
                Button("Scegli…") { Task { await model.chooseExportDirectory() } }.buttonStyle(QuietButton())
            }
            Button("Apri") { model.openDirectory(path) }.buttonStyle(QuietButton()).accessibilityLabel("Apri \(title)")
        }
    }
}
