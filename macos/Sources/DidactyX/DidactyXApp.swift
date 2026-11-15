import AppKit
import SwiftUI

@MainActor
final class AppDelegate: NSObject, NSApplicationDelegate {
    weak var model: AppModel?
    private var terminating = false

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }

    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply {
        guard !terminating, let model else { return .terminateNow }
        terminating = true
        Task {
            let saved = await model.flush()
            if !saved {
                let alert = NSAlert()
                alert.messageText = "Ci sono modifiche non salvate"
                alert.informativeText = "\(model.errorMessage ?? "Il salvataggio non è riuscito.") Puoi tornare al programma e riprovare."
                alert.addButton(withTitle: "Continua a modificare")
                alert.addButton(withTitle: "Esci senza salvare")
                if alert.runModal() != .alertSecondButtonReturn {
                    terminating = false
                    sender.reply(toApplicationShouldTerminate: false)
                    return
                }
            }
            await model.engine.stop()
            sender.reply(toApplicationShouldTerminate: true)
        }
        return .terminateLater
    }
}

@main
@MainActor
struct DidactyXApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var delegate
    @StateObject private var model = AppModel()

    var body: some Scene {
        Window("DidactyX", id: "main") {
            RootView().environmentObject(model)
                .onAppear {
                    delegate.model = model
                    NSApplication.shared.activate(ignoringOtherApps: true)
                }
        }
        .defaultSize(width: 1140, height: 780)
        .windowStyle(.hiddenTitleBar)
        .commands {
            CommandGroup(replacing: .newItem) {
                Button("Nuovo programma") { model.showNewProgram = true }
                    .keyboardShortcut("n").disabled(!model.ready)
            }
            CommandGroup(replacing: .appSettings) {
                Button("Impostazioni…") { model.showSettings = true }.keyboardShortcut(",")
            }
            CommandGroup(after: .saveItem) {
                Button("Salva modifiche") { Task { await model.flush() } }.keyboardShortcut("s")
            }
        }
    }
}
