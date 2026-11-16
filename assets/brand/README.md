# Identità visiva di DidactyX

La UI 0.3.1 adotta una base nero-viola, accenti menta, violetto e magenta, superfici sobrie e tipografia monospaziata per i metadati. Il colore distingue azioni, selezione e identità; il testo didattico mantiene il proprio impaginato chiaro.

## Marchio

Quattro facce angolari, ispirate a pagine ripiegate, formano una X intorno a un nodo centrale. Le diagonali menta e violetto distinguono il segno anche alle dimensioni della barra laterale. Il nome è composto come DidactyX, con la X evidenziata in violetto.

- [didactyx-mark.svg](didactyx-mark.svg): simbolo vettoriale su fondo trasparente, destinato a superfici scure.
- [didactyx-icon.svg](didactyx-icon.svg): simbolo con piastrella scura.
- [didactyx-icon-preview.png](didactyx-icon-preview.png): anteprima PNG di 512 × 512 pixel.

La sorgente autorevole della geometria e dei gradienti è `macos/Sources/DidactyX/BrandArtwork.swift`. SwiftUI, generatore delle icone macOS e master SVG usano la stessa definizione. Il marchio non dipende da un font o da un'immagine remota. Il nome nell'interfaccia usa il font di sistema.

## Palette

| Colore | Valore | Utilizzo |
| --- | --- | --- |
| Nero-viola | `#0D0B14` | Sfondo |
| Viola scuro | `#171321` | Pannelli |
| Viola rialzato | `#231C31` | Superfici attive |
| Bordo | `#393047` | Separazione delle superfici |
| Menta | `#57F2CE` | Azioni principali e selezioni |
| Violetto | `#AB92FF` | Marchio, classi, focus e accenti |
| Magenta | `#F47ACB` | Dettagli del marchio e delle schede |
| Testo | `#F4F0FB` | Testo principale |
| Secondario | `#ABA2BC` | Descrizioni e metadati |
| Ambra | `#FFD08A` | Avvisi |

Il tema è in `macos/Sources/DidactyX/Theme.swift`: sfumature statiche leggere, separatori sottili, pulsanti menta con ombra contenuta e schede con bordo violetto al passaggio del puntatore. La selezione della navigazione è indicata anche da una barra laterale. I campi mostrano un bordo violetto quando ricevono il focus.

## Rigenerazione degli asset

Dalla radice del repository:

```sh
mkdir -p tmp
swiftc macos/Sources/DidactyX/BrandArtwork.swift scripts/make_icon.swift -o tmp/make-icon
tmp/make-icon tmp/app-icon.iconset assets/brand
cp tmp/app-icon.iconset/icon_256x256@2x.png assets/brand/didactyx-icon-preview.png
```

`bash scripts/build_macos.sh` genera e include automaticamente l'icona `.icns` nel pacchetto. La build non riscrive i master versionati. Le dimensioni dell'iconset vanno da 16 pixel a 1024 pixel.

## Verifica

Build release e firma locale verificate su macOS arm64. Controllo visivo nativo di home, scheda del programma, modulo di creazione con focus, navigazione selezionata e lettore della lezione. Il modulo di prova è stato chiuso senza creare programmi. Il pilota salvato è stato riaperto correttamente. I 36 test esistenti e l'integrazione Swift con il motore incluso sono stati rieseguiti senza chiamate generative.
