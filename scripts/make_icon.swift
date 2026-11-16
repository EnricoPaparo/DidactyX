import AppKit
import Foundation

@main
enum MakeIcon {
    static func main() throws {
        let output = URL(fileURLWithPath: CommandLine.arguments[1])
        try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
        for size in [16, 32, 128, 256, 512] {
            for scale in [1, 2] {
                let pixels = size * scale
                let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: pixels, pixelsHigh: pixels,
                    bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                    colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
                NSGraphicsContext.saveGraphicsState()
                NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmap)
                let context = NSGraphicsContext.current!.cgContext
                context.translateBy(x: 0, y: CGFloat(pixels)); context.scaleBy(x: 1, y: -1)
                BrandArtwork.draw(in: context, size: CGFloat(pixels), tile: true)
                NSGraphicsContext.restoreGraphicsState()
                let name = "icon_\(size)x\(size)\(scale == 2 ? "@2x" : "").png"
                try bitmap.representation(using: .png, properties: [:])!.write(to: output.appendingPathComponent(name))
            }
        }
        if CommandLine.arguments.count > 2 {
            let masters = URL(fileURLWithPath: CommandLine.arguments[2])
            try FileManager.default.createDirectory(at: masters, withIntermediateDirectories: true)
            try BrandArtwork.svg(tile: false).write(to: masters.appendingPathComponent("didactyx-mark.svg"), atomically: true, encoding: .utf8)
            try BrandArtwork.svg(tile: true).write(to: masters.appendingPathComponent("didactyx-icon.svg"), atomically: true, encoding: .utf8)
        }
    }
}
