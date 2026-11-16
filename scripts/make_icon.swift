import AppKit
import Foundation

let output = URL(fileURLWithPath: CommandLine.arguments[1])
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
for size in [16, 32, 128, 256, 512] {
    for scale in [1, 2] {
        let pixels = size * scale
        let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: pixels, pixelsHigh: pixels,
                                      bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true,
                                      isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
        NSGraphicsContext.saveGraphicsState()
        NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmap)
        let p = CGFloat(pixels)
        NSColor(calibratedRed: 0.045, green: 0.065, blue: 0.085, alpha: 1).setFill()
        NSBezierPath(roundedRect: NSRect(x: p * 0.06, y: p * 0.06, width: p * 0.88, height: p * 0.88), xRadius: p * 0.2, yRadius: p * 0.2).fill()
        let symbol = NSBezierPath()
        symbol.move(to: NSPoint(x: p * 0.28, y: p * 0.66))
        symbol.line(to: NSPoint(x: p * 0.46, y: p * 0.5))
        symbol.line(to: NSPoint(x: p * 0.28, y: p * 0.34))
        symbol.move(to: NSPoint(x: p * 0.54, y: p * 0.34))
        symbol.line(to: NSPoint(x: p * 0.73, y: p * 0.34))
        symbol.lineWidth = max(1, p * 0.055)
        symbol.lineCapStyle = .round
        symbol.lineJoinStyle = .round
        NSColor(calibratedRed: 0.36, green: 0.87, blue: 0.91, alpha: 1).setStroke()
        symbol.stroke()
        NSGraphicsContext.restoreGraphicsState()
        let name = "icon_\(size)x\(size)\(scale == 2 ? "@2x" : "").png"
        try bitmap.representation(using: .png, properties: [:])!.write(to: output.appendingPathComponent(name))
    }
}
