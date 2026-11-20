extends Node2D

const FACE_DIR := "res://art/face/"
const BODY_DIR := "res://art/body/"
const IRIS_SHADER = preload("res://eye.gdshader")
const GRIP := Vector2(4, 44)
const UPPER_ARM := 147.0
const LOWER_ARM := 129.0
const THIGH := 315.0
const CALF := 310.0
const SHOULDER_FAR := Vector2(-92, -224)
const SHOULDER_NEAR := Vector2(102, -217)
const HIP_FAR := Vector2(-45, 17)
const HIP_NEAR := Vector2(42, 16)
const ANKLE_FROM_HEEL := Vector2(22, -62)

var face_parts: Dictionary
var body_parts: Dictionary
var torso: Node2D
var head: Node2D
var hair: Array[Node2D] = []
var eyes: Array[Node2D] = []
var iris: Array[Sprite2D] = []
var iris_origin: Array[Vector2] = []
var brow: Array[Node2D] = []
var closed: Array[Line2D] = []
var lips: Sprite2D
var mouth: Mouth
var blush: Cheeks
var near_arm: Dictionary
var far_arm: Dictionary
var near_leg: Dictionary
var far_leg: Dictionary


class Mouth extends Node2D:
	var amount := 0.0
	var form := Vector2(1, 1)
	var corner := 0.0

	func _draw() -> void:
		if amount < .015:
			return
		var w := 29.0 * form.x
		var h := 18.0 * amount * form.y
		var left := Vector2(-w, 5 - corner)
		var right := Vector2(w, -7 - corner)
		var top := Vector2(-.05 * w, -5 - h * .18)
		var low := Vector2(.08 * w, 6 + h * .86)
		var outline := loop([left, top, right, low])
		draw_colored_polygon(outline, Color("#a4433b"))
		draw_polyline(outline,Color("#a4433b"),1.0,true)
		var inner_top := top + Vector2(0, 3.5)
		var inside_low := low - Vector2(0, 3.5)
		draw_colored_polygon(loop([left.lerp(top,.12), inner_top, right.lerp(top,.13), inside_low]),
			Color("#3e181d"))
		if amount > .24 and form.x > .72:
			var teeth := PackedVector2Array([
				left.lerp(inner_top,.22), inner_top, right.lerp(inner_top,.22),
				right.lerp(inner_top,.37) + Vector2(0,2),
				inner_top + Vector2(0, min(6.0, h*.34)),
				left.lerp(inner_top,.37) + Vector2(0,2)])
			var teeth_color := Color("#f2cdb3")
			draw_colored_polygon(teeth, teeth_color)
			draw_polyline(PackedVector2Array([teeth[0],teeth[1],teeth[2]]), teeth_color, .75, true)
		if h > 7:
			draw_colored_polygon(loop([Vector2(-w*.48, h*.52),Vector2(w*.18,h*.37),
				Vector2(w*.55,h*.39),inside_low]), Color("#8e4147"))
		draw_polyline(PackedVector2Array([Vector2(-w*.3,low.y-1),Vector2(w*.02,low.y+.2),
			Vector2(w*.26,low.y-.7)]),Color(1.0,.63,.50,.68),1.45,true)

	func loop(knots: Array) -> PackedVector2Array:
		var polygon := PackedVector2Array()
		for i in knots.size():
			var a: Vector2 = knots[(i + knots.size() - 1) % knots.size()]
			var b: Vector2 = knots[i]
			var c: Vector2 = knots[(i + 1) % knots.size()]
			var d: Vector2 = knots[(i + 2) % knots.size()]
			for step in 10:
				var t := step / 10.0
				polygon.append(b.cubic_interpolate(c,a,d,t))
		return polygon


class Cheeks extends Node2D:
	var lift := 0.0
	func _draw() -> void:
		for i in 7:
			var size_factor := 1.0 - i * .115
			draw_set_transform(Vector2(-31,-64-lift*2), -.20, Vector2(1.0,.51))
			draw_circle(Vector2.ZERO, 20 * size_factor, Color(.76,.21,.19,.020*lift),true,-1,true)
			draw_set_transform(Vector2(44,-81-lift*2), -.25, Vector2(1.0,.48))
			draw_circle(Vector2.ZERO, 15 * size_factor, Color(.76,.21,.19,.021*lift),true,-1,true)


func _ready() -> void:
	face_parts = read_json(FACE_DIR + "layout.json")
	var body_layout := read_json(BODY_DIR + "layout.json")
	body_parts = body_layout["parts"]
	far_leg = make_leg(0)
	near_leg = make_leg(1)
	far_arm = make_arm(1)
	torso = pivot(self)
	part(torso, BODY_DIR, body_parts["torso"]).z_index = 2
	near_arm = make_arm(4)
	make_face()


func read_json(path: String) -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(path))


func xy(values: Array) -> Vector2:
	return Vector2(values[0], values[1])


func pivot(parent: Node2D, at := Vector2.ZERO) -> Node2D:
	var node := Node2D.new()
	node.position = at
	parent.add_child(node)
	return node


func part(parent: Node2D, directory: String, art: Dictionary) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = load(directory + art["file"])
	sprite.centered = false
	sprite.position = xy(art["offset"])
	parent.add_child(sprite)
	return sprite


func body_part(parent: Node2D, name: String, depth: int) -> Sprite2D:
	var sprite := part(parent, BODY_DIR, body_parts[name])
	sprite.z_index = depth
	return sprite


func face_part(parent: Node2D, name: String) -> Sprite2D:
	return part(parent, FACE_DIR, face_parts[name])


func face_pivot(parent: Node2D, name: String) -> Node2D:
	return pivot(parent, xy(face_parts[name]["pivot"]))


func make_arm(depth: int) -> Dictionary:
	var upper := pivot(self)
	var forearm := pivot(self)
	var hand := pivot(self)
	body_part(upper, "upper_arm", depth)
	body_part(forearm, "forearm", depth)
	return {
		"upper": upper, "forearm": forearm, "hand": hand,
		"open": body_part(hand, "hand_open", depth),
		"back": body_part(hand, "hand_grip_back", depth),
		"thumb": body_part(hand, "hand_grip_front", depth + 3)
	}


func make_leg(depth: int) -> Dictionary:
	var thigh := pivot(self)
	var calf := pivot(self)
	var shoe := pivot(self)
	body_part(thigh, "upper_leg", depth)
	body_part(calf, "lower_leg", depth)
	body_part(shoe, "shoe", depth)
	if depth == 0:
		thigh.modulate = Color(.86, .79, .73)
		calf.modulate = Color(.86, .79, .73)
		shoe.modulate = Color(.82, .71, .70)
	return {"thigh": thigh, "calf": calf, "shoe": shoe}


func make_face() -> void:
	head = pivot(torso, Vector2(10, -266))
	head.z_index = 3
	for name in ["hair_far", "hair_near"]:
		var lock := face_pivot(head, name)
		face_part(lock, name)
		hair.append(lock)
	face_part(head,"head_skin")
	blush = Cheeks.new()
	head.add_child(blush)
	for side in ["left", "right"]:
		var eye := face_pivot(head, "eye_" + side + "_mask")
		var eyeball := face_part(eye, "eye_" + side + "_mask")
		var iris_mat := ShaderMaterial.new()
		iris_mat.shader = IRIS_SHADER
		iris_mat.set_shader_parameter("dimensions", eyeball.texture.get_size())
		eyeball.material = iris_mat
		var iris_pivot := Vector2(-.3, 1.1) if side == "left" else Vector2(-9.5, 1.1)
		iris_origin.append(iris_pivot - eyeball.position)
		iris.append(eyeball)
		face_part(eye, "eye_" + side + "_liner")
		eyes.append(eye)
		var lash := Line2D.new()
		lash.position = eye.position
		lash.points = PackedVector2Array([Vector2(-23, 5),Vector2(-14, 1),Vector2(-4,-1),Vector2(6,-2),
			Vector2(16,-1),Vector2(25,1)]) if side == "left" else PackedVector2Array([
			Vector2(-16,7),Vector2(-9,2),Vector2(0,-1),Vector2(9,-3),Vector2(17,-6),Vector2(22,-9)])
		lash.width = 2.4
		lash.antialiased = true
		lash.default_color = Color("#301611")
		head.add_child(lash)
		closed.append(lash)
		var brow_root := face_pivot(head, "brow_" + side)
		face_part(brow_root, "brow_" + side)
		brow.append(brow_root)
	lips = face_part(face_pivot(head, "lips"), "lips")
	mouth = Mouth.new()
	mouth.position = xy(face_parts["lips"]["pivot"])
	head.add_child(mouth)


func limb_joint(start: Vector2, target: Vector2, a: float, b: float, bend: float) -> Vector2:
	var delta := target - start
	var direction := delta.normalized() if delta.length_squared() > .001 else Vector2.DOWN
	var span := clampf(delta.length(), absf(a-b)+.2, a+b-.2)
	var along := (span*span + a*a - b*b) / (2*span)
	var across := sqrt(maxf(0, a*a-along*along)) * bend
	return start + direction*along + direction.orthogonal()*across


func aim(part_node: Node2D, from: Vector2, to: Vector2) -> void:
	part_node.position = from
	part_node.rotation = (to-from).angle() - PI/2


func pose_leg(leg: Dictionary, hip: Vector2, heel: Vector2, pitch: float) -> void:
	var ankle := heel + ANKLE_FROM_HEEL.rotated(pitch)
	var knee := limb_joint(hip, ankle, THIGH, CALF, 1)
	aim(leg["thigh"], hip, knee)
	aim(leg["calf"], knee, ankle)
	leg["shoe"].position = heel
	leg["shoe"].rotation = pitch


func pose_arm(arm: Dictionary, shoulder: Vector2, wrist: Vector2, angle: float,
		pinch: float, bend: float) -> void:
	var elbow := limb_joint(shoulder,wrist,UPPER_ARM,LOWER_ARM,bend)
	aim(arm["upper"],shoulder,elbow)
	aim(arm["forearm"],elbow,wrist)
	arm["hand"].position = wrist
	arm["hand"].rotation = angle
	arm["open"].visible = pinch <= .12
	arm["back"].visible = pinch > .12
	var thumb: Sprite2D = arm["thumb"]
	thumb.visible = pinch > .12
	thumb.position = xy(body_parts["hand_grip_front"]["offset"]) + Vector2(3,-27)*(1.0-pinch)
	thumb.rotation = -.26*(1.0-pinch)


func pose_body(lean: float, far_heel: Vector2, near_heel: Vector2, far_pitch: float,
		near_pitch: float, far_wrist: Vector2, near_wrist: Vector2, hand_angle: float, pinch: float) -> void:
	torso.rotation = lean
	pose_leg(far_leg, HIP_FAR, far_heel, far_pitch)
	pose_leg(near_leg, HIP_NEAR, near_heel, near_pitch)
	pose_arm(far_arm, SHOULDER_FAR.rotated(lean), far_wrist, .12, 0, 1)
	pose_arm(near_arm, SHOULDER_NEAR.rotated(lean), near_wrist, hand_angle, pinch, -1)


func pose_face(angle: float, tilt: float, gaze: Vector2, blink: float, brows: Vector2,
		cheek: float, opening: float, form: Vector2, hair_sway: float) -> void:
	head.rotation = angle
	head.position = Vector2(10, -266 + tilt)
	hair[0].rotation = hair_sway
	hair[1].rotation = -hair_sway * .57
	blush.lift = cheek
	blush.queue_redraw()
	for i in 2:
		var original_size := iris[i].texture.get_size()
		var look := iris_origin[i] + Vector2(gaze.x * (1.0 if i == 0 else .87),gaze.y)
		iris[i].material.set_shader_parameter("iris_center", look / original_size)
		eyes[i].scale.y = maxf(.10, blink)
		eyes[i].visible = blink > .24
		closed[i].visible = blink <= .24
		brow[i].position.y = xy(face_parts["brow_" + ("left" if i == 0 else "right")]["pivot"]).y + brows[i]
		brow[i].rotation = -brows[i] * (.012 if i == 0 else -.010)
	lips.modulate.a = 1.0 - smoothstep(.04,.24,opening)
	mouth.amount = opening
	mouth.form = form
	mouth.corner = cheek * 2.2
	mouth.queue_redraw()
