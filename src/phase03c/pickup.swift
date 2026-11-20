import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

// Local, frame-addressable shot compositor. Launch at repository root.
let width = 1080, height = 1920
let space = CGColorSpace(name: CGColorSpace.sRGB)!
let baseArt = "src/phase02/art/"
let lipstick = readImage(baseArt + "lipstick.png")
let room = readImage(baseArt + "room_clean_plate.png")
let nativeVanity = room.cropping(to: CGRect(x: 1320, y: 532, width: 67, height: 38))!
let pinkWall = room.cropping(to: CGRect(x: 1316, y: 442, width: 13, height: 36))!
let secondShot = 24
let contactFrame = 59
let liftFrame = 63
let frameCount = 108

func readImage(_ path: String) -> CGImage {
    let url = URL(fileURLWithPath: path)
    guard let input = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(input, 0, nil) else {
        fatalError("Kaynak açılamadı: \(path)")
    }
    return image
}
func context(_ w: Int, _ h: Int) -> CGContext {
    let c = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8,
                      bytesPerRow: w * 4, space: space,
                      bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    c.translateBy(x: 0, y: CGFloat(h))
    c.scaleBy(x: 1, y: -1)
    c.interpolationQuality = .high
    return c
}
func rect(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat) -> CGRect {
    CGRect(x: x, y: y, width: w, height: h)
}
func point(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: x, y: y) }
func color(_ rgb: UInt32, _ alpha: CGFloat = 1) -> CGColor {
    CGColor(srgbRed: CGFloat((rgb >> 16) & 255)/255, green: CGFloat((rgb >> 8) & 255)/255,
            blue: CGFloat(rgb & 255)/255, alpha: alpha)
}
func drawImage(_ c: CGContext, _ image: CGImage, _ destination: CGRect, alpha: CGFloat = 1) {
    c.saveGState()
    c.translateBy(x: destination.minX, y: destination.maxY)
    c.scaleBy(x: 1, y: -1)
    c.setAlpha(alpha)
    c.draw(image, in: rect(0, 0, destination.width, destination.height))
    c.restoreGState()
}
func gradient(_ c: CGContext, _ start: CGPoint, _ end: CGPoint, _ colors: [CGColor],
              _ positions: [CGFloat]? = nil) {
    let g = CGGradient(colorsSpace: space, colors: colors as CFArray, locations: positions)!
    c.drawLinearGradient(g, start: start, end: end,
                         options: [.drawsBeforeStartLocation, .drawsAfterEndLocation])
}
func path(_ commands: [[CGFloat]], close: Bool = true) -> CGPath {
    let p = CGMutablePath()
    p.move(to: point(commands[0][0], commands[0][1]))
    for s in commands.dropFirst() {
        if s.count == 2 { p.addLine(to: point(s[0], s[1])) }
        else if s.count == 4 {
            p.addQuadCurve(to: point(s[2], s[3]), control: point(s[0], s[1]))
        } else {
            p.addCurve(to: point(s[4], s[5]), control1: point(s[0], s[1]), control2: point(s[2], s[3]))
        }
    }
    if close { p.closeSubpath() }
    return p
}
func fill(_ c: CGContext, _ p: CGPath, _ rgb: UInt32, opacity: CGFloat = 1) {
    c.setFillColor(color(rgb, opacity)); c.addPath(p); c.fillPath()
}
func stroke(_ c: CGContext, _ p: CGPath, _ rgb: UInt32, _ width: CGFloat, opacity: CGFloat = 1) {
    c.setStrokeColor(color(rgb, opacity)); c.setLineWidth(width); c.setLineJoin(.round)
    c.setLineCap(.round); c.addPath(p); c.strokePath()
}
func painted(_ c: CGContext, _ p: CGPath, _ colors: [UInt32], _ y: CGFloat, _ h: CGFloat,
             outline: UInt32 = 0x85463c, line: CGFloat = 3.2) {
    c.saveGState(); c.addPath(p); c.clip()
    gradient(c, point(0, y), point(0, y + h), colors.map { color($0) })
    c.restoreGState()
    stroke(c, p, outline, line)
}
func oval(_ c: CGContext, _ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat,
          _ rgb: UInt32, _ alpha: CGFloat) {
    c.setFillColor(color(rgb, alpha)); c.fillEllipse(in: rect(x,y,w,h))
}
func softOval(_ c: CGContext, _ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat,
              _ rgb: UInt32, _ alpha: CGFloat) {
    for i in 0..<13 {
        let shrink = CGFloat(i) * 0.051
        let ringW = w * (1 - shrink), ringH = h * (1 - shrink)
        oval(c, x-ringW/2, y-ringH/2, ringW, ringH, rgb, alpha/13)
    }
}
func plate(_ c: CGContext, shot2: Bool) {
    drawImage(c, pinkWall, rect(-50, -80, 1180, 1410))
    gradient(c, point(40, 0), point(1010, 1190),
             [color(0x7e304e,0.55), color(0xdd7987,0.16), color(0xffbb9b,0.26)])
    // Same vanity lacquer, pink marble front and warm reflected lamps.
    let tableTop: CGFloat = shot2 ? 1232 : 1272
    drawImage(c, nativeVanity, rect(-52, tableTop-22, 1180, 781))
    gradient(c, point(0, tableTop+4), point(0, 1890),
             [color(0xe2a08b,0.32),color(0xf8e2ca,0.18),color(0x8a414f,0.21)])
    c.setFillColor(color(0xffd4ae, 0.17))
    c.fill(rect(0, tableTop-10, 1080, 10))
    softOval(c, 614, tableTop+103, 920, 225, 0xffe3b2, 0.26)
}
func tube(_ c: CGContext, x: CGFloat, y: CGFloat, s: CGFloat, rotation: CGFloat) {
    c.saveGState()
    c.translateBy(x: x, y: y)
    c.rotate(by: rotation)
    drawImage(c, lipstick, rect(-14.5*s, -54.5*s, 28*s, 92*s))
    c.restoreGState()
}
let skin: [UInt32] = [0xffd2a3, 0xf2a378, 0xc36552]
let skinEdge: UInt32 = 0x7d443b
func nail(_ c: CGContext, _ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ angle: CGFloat) {
    c.saveGState(); c.translateBy(x: x, y: y); c.rotate(by: angle)
    let n = path([[0,h*0.49],[w*0.25,-h*0.48,w*0.81,-h*0.53,w,0],
                  [w*0.82,h*0.44,w*0.37,h*0.62,0,h*0.49]])
    painted(c,n,[0xc84c5e,0x8d203e,0x531629],-h/2,h,outline:0x65172b,line:1.7)
    stroke(c,path([[w*0.27,-h*0.12],[w*0.58,-h*0.24]],close:false),0xffa59b,1.8,opacity:0.8)
    c.restoreGState()
}
func behindHand(_ c: CGContext, close: CGFloat) {
    let rear = path([[665,-52],[585,-48,369,-42,256,-28],[220,-24,188,-31,160,-50],
                     [125,-65,90,-63,70,-42],[41,-24,7,31,17,62],
                     [45,91,83,97,129,76],[166,66,188,43,216,43],
                     [335,53,510,88,665,99]])
    painted(c,rear,skin,-60,150,outline:skinEdge)
    fill(c,path([[214,30],[354,42,502,69,665,76],[665,97],
                 [488,90,342,56,219,46],[175,46,154,72,119,81],
                 [132,64,157,48,181,35],[199,29]]),0xba6253,opacity:0.48)
    fill(c,path([[222,-21],[345,-27,497,-36,660,-40],[660,-25],
                 [530,-14,355,-20,222,-10]]),0xffdabc,opacity:0.5)
    // From the far palm four separately shaded fingers fold around the body.
    let fingerData: [(CGFloat, CGFloat, CGFloat)] = [(-68, 23, 0),(-35,27,5),(-3,25,16),(27,21,35)]
    for (i, data) in fingerData.enumerated().reversed() {
        let (dy, thick, setback) = data
        let fingertip = -102 + setback + 59*close
        let bend = CGFloat(i-1)*5 + close*16
        let shell = path([[104,dy+13],[61,dy-10,21,dy-9,-13,dy-5],
                          [fingertip+26,dy+bend-8,fingertip+1,dy+bend-10,fingertip,dy+bend],
                          [fingertip-6,dy+bend+thick*0.52,fingertip+4,dy+bend+thick,fingertip+16,dy+bend+thick],
                          [fingertip+36,dy+bend+thick+3,0,dy+thick+5,27,dy+thick+8],
                          [58,dy+thick+15,80,dy+thick+12,111,dy+thick+10]])
        let softEdge = i == 0 ? 0x925246 : 0x8d4f45
        painted(c,shell,[0xffd5a9,0xf2a174,0xd18061],dy-10,thick+35,outline:UInt32(softEdge),line:2.6)
        nail(c,fingertip+13,dy+bend+3,26,thick*0.65,CGFloat.pi)
        stroke(c,path([[fingertip+34,dy+bend+14],[fingertip+52,dy+bend+11]],close:false),
               0xa65c50,1.7,opacity:0.62)
    }
    let palmShade = path([[149,-47],[108,-58,77,-43,68,-18],[91,-21,111,-25,146,-25],
                          [164,-24,181,-24,199,-20],[183,-35,164,-45,149,-47]])
    fill(c,palmShade,0xffc197,opacity:0.83)
    stroke(c,path([[176,36],[151,35,130,38,113,42],[101,56]],close:false),0x9a5548,2.4,opacity:0.75)
    watch(c)
}
func watch(_ c: CGContext) {
    c.saveGState(); c.translateBy(x: 226, y: 5); c.rotate(by: -0.08)
    let band = path([[-29,-43],[9,-53,42,-46,53,-37],[53,31],[40,51,0,52,-24,39]])
    painted(c,band,[0xffeabd,0xcd803c,0xf3b956,0x895427],-48,98,outline:0x6b4526,line:2.8)
    for y in [-33,-16,20,35] {
        stroke(c,path([[-22,CGFloat(y)],[13,CGFloat(y)-3,37,CGFloat(y)-1,47,CGFloat(y)+2]],close:false),
               0x965a2b,2.7)
        stroke(c,path([[-19,CGFloat(y)-4],[16,CGFloat(y)-6,39,CGFloat(y)-4,46,CGFloat(y)-1]],close:false),
               0xffe7a1,1.4)
    }
    let rim = CGPath(roundedRect: rect(-39,-31,73,58),cornerWidth:8,cornerHeight:8,transform:nil)
    painted(c,rim,[0xffe6a2,0xa96428,0xfecd6a,0x9d5826],-31,57,outline:0x704023,line:3)
    let inner = CGPath(roundedRect: rect(-31,-23,57,42),cornerWidth:4,cornerHeight:4,transform:nil)
    painted(c,inner,[0xffffe3,0xe5bb73,0xffedbe],-23,42,outline:0xa86f38,line:2)
    for x: CGFloat in [-24,-14,-4,6,16] {
        stroke(c,path([[x,-19],[x,-15]],close:false),0x7d542a,1.4)
        stroke(c,path([[x,12],[x,15]],close:false),0x7d542a,1.4)
    }
    stroke(c,path([[-3,4],[-3,-12]],close:false),0x79552c,2)
    stroke(c,path([[-3,4],[10,0]],close:false),0x79552c,2)
    oval(c,-5,2,4,4,0x94602d,1)
    fill(c,path([[-30,-23],[-22,-23],[18,17],[5,18]]),0xffffff,opacity:0.18)
    c.restoreGState()
}
func frontThumb(_ c: CGContext, close: CGFloat) {
    let tip = 3-42*close
    let dy = 28-49*close
    let thumb = path([[152,54],[121,52,108,39,93,22],
                      [75,17,55,23,35,20],[16,18,tip+21,dy+25,tip+10,dy+25],
                      [tip-2,dy+27,tip-9,dy+16,tip-3,dy+4],
                      [tip+7,dy-10,tip+32,dy-11,tip+45,dy-8],
                      [tip+69,dy-5,93,dy-1,113,5],[131,8,150,26,154,43]])
    painted(c,thumb,[0xffdcb4,0xf4a681,0xce785d],dy-12,81,outline:skinEdge,line:3)
    nail(c,tip+28,dy+5,32,19,CGFloat.pi+0.06)
    stroke(c,path([[tip+44,dy+17],[tip+60,dy+18,tip+67,dy+16,tip+76,dy+15]],close:false),
           0x9d5548,2.4,opacity:0.59)
    stroke(c,path([[109,11],[128,21,136,34,141,40]],close:false),0xffcfab,2.8,opacity:0.68)
}
func hand(_ c: CGContext, x: CGFloat, y: CGFloat, close: CGFloat, angle: CGFloat, front: Bool) {
    c.saveGState(); c.translateBy(x: x,y: y); c.rotate(by: angle)
    c.scaleBy(x: 1.53, y: 1.45)
    if front { frontThumb(c,close:close) } else { behindHand(c,close:close) }
    c.restoreGState()
}
func blend(_ a: CGFloat,_ b: CGFloat,_ t: CGFloat) -> CGFloat { a+(b-a)*t }
func smooth(_ frame: Int,_ first: Int,_ last: Int) -> CGFloat {
    let x = CGFloat(max(0,min(frame-first,last-first)))/CGFloat(last-first)
    return x*x*(3-2*x)
}
func render(_ frame: Int) -> CGImage {
    let c = context(width,height)
    let hasHand = frame >= secondShot
    plate(c,shot2:hasHand)
    let startX: CGFloat = hasHand ? 506 : 542
    let startY: CGFloat = hasHand ? 1067 : 1081
    let scale: CGFloat = hasHand ? 5.6 : 7.1
    let rise = smooth(frame,liftFrame,92)
    let settle = smooth(frame,92,103)
    let rotation = CGFloat.pi/12 * rise
    let heroX = startX + 52*rise + 3*settle
    let heroY = startY - 246*rise + 7*settle
    let baseY = startY + 34.7*scale
    // Soft color reflection, rather than a readable second silhouette.
    softOval(c,heroX+4,baseY+30,81,74,0xa86860,0.12*(1-rise))
    softOval(c,heroX,baseY+16,97,29,0xe4aa61,0.17*(1-rise))
    softOval(c,heroX+4,baseY+3,132+rise*62,46+rise*15,0x833c45,0.37-0.29*rise)
    softOval(c,heroX-1,baseY+4,99,16,0x622833,0.46*(1-rise))
    if !hasHand {
        tube(c,x:heroX,y:heroY,s:scale,rotation:rotation)
        return c.makeImage()!
    }
    let reach = smooth(frame,secondShot+5,contactFrame)
    let grasp = smooth(frame,51,liftFrame)
    let handX = blend(1204,startX,reach) + (heroX-startX)
    let handY = blend(startY+154,startY,reach) + (heroY-startY)
    let angle = blend(-0.13,0,reach) + rotation
    softOval(c,handX+104,baseY+22,300+80*rise,67+42*rise,0x985b54,(0.13-0.08*rise)*reach)
    hand(c,x:handX,y:handY,close:grasp,angle:angle,front:false)
    tube(c,x:heroX,y:heroY,s:scale,rotation:rotation)
    // The approaching thumb stays on the near side of the stationary tube.
    hand(c,x:handX,y:handY,close:grasp,angle:angle,front:true)
    return c.makeImage()!
}
func save(_ image: CGImage, _ file: String) {
    let url = URL(fileURLWithPath:file)
    try! FileManager.default.createDirectory(at:url.deletingLastPathComponent(),
                                             withIntermediateDirectories:true)
    let output = CGImageDestinationCreateWithURL(url as CFURL,UTType.png.identifier as CFString,1,nil)!
    CGImageDestinationAddImage(output,image,nil)
    precondition(CGImageDestinationFinalize(output))
}
let settings = Array(CommandLine.arguments.dropFirst())
if settings.first == "--starts" {
    save(render(0),"outputs/phase03c/start_plan01.png")
    save(render(secondShot),"outputs/phase03c/start_plan02.png")
    if settings.count > 1 { save(render(frameCount-1),settings[1]) }
} else if settings.first == "--still" && settings.count == 3 {
    save(render(Int(settings[1])!),settings[2])
} else if settings.count == 1 {
    for frame in 0..<frameCount {
        autoreleasepool {
            save(render(frame),settings[0]+"/"+String(format:"p%03d.png",frame))
        }
    }
} else {
    fatalError("swift src/phase03c/pickup.swift --starts | <kare-klasörü>")
}
