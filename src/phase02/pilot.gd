extends Node2D

const Rig = preload("res://lalin_rig.gd")
const ART := "res://art/"
const CUT := 66
const GRAB := 112
const LIFT := 116
const PLACE := 282
const RELEASE := 283

const VOWELS := {
	"rest": Vector3(0,1,1),
	"closed": Vector3(.012,.88,.66),
	"a": Vector3(.81,.91,1.0),
	"e": Vector3(.37,1.02,.65),
	"i": Vector3(.31,1.04,.48),
	"o": Vector3(.60,.59,1.02),
	"u": Vector3(.41,.51,.81),
}

var room: Dictionary
var timeline: Dictionary
var dialogue: Dictionary
var actor: Rig
var walk: Node2D
var vanity: Node2D
var lipstick: Sprite2D
var prop_point: Vector2
var prop_base: Vector2
var floor_shadows: Array[Shadow] = []
var lipstick_shadow: Shadow
var preview_audio: Array[AudioStreamPlayer] = []
var elapsed := 0.0
var previous := -1
var audio_on := true
var rendering := false


class Shadow extends Node2D:
	var radii := Vector2(20,5)
	var strength := .20
	func _draw() -> void:
		for pass_index in 8:
			var weight := 1.0 - pass_index * .103
			draw_set_transform(Vector2.ZERO,0,Vector2(radii.x*weight,radii.y*weight))
			draw_circle(Vector2.ZERO,1,Color(.22,.104,.154,strength*.18),true,-1,true)


func _ready() -> void:
	room = read_json("res://art/room_layout.json")
	timeline = read_json("res://events.json")
	dialogue = read_json("res://dialogue.json")
	audio_on = FileAccess.file_exists("res://../../assets/voice/raina_pilot_line.mp3")
	build_set()
	actor = Rig.new()
	actor.name = "LalinRig"
	add_child(actor)
	apply_frame(0)

	var arguments := OS.get_cmdline_user_args()
	if arguments.size() >= 2 and arguments[0] == "--frames":
		rendering = true
		var frame_numbers: Array = range(int(timeline["frames"]))
		if arguments.size() > 2:
			frame_numbers = []
			for index in range(2, arguments.size()):
				frame_numbers.append(int(arguments[index]))
		write_frames.call_deferred(arguments[1], frame_numbers)
	else:
		prepare_audio()


func read_json(path: String) -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(path))


func xy(values: Array) -> Vector2:
	return Vector2(values[0], values[1])


func sprite(parent: Node2D, path: String, depth: int) -> Sprite2D:
	var node := Sprite2D.new()
	node.texture = load(ART + path)
	node.centered = false
	node.z_index = depth
	parent.add_child(node)
	return node


func build_set() -> void:
	walk = Node2D.new()
	walk.name = "Window"
	add_child(walk)
	sprite(walk, room["walk"]["background"], -10)
	sprite(walk, room["walk"]["foreground"], 8)
	for index in 3:
		var shadow := Shadow.new()
		shadow.z_index = -4
		walk.add_child(shadow)
		floor_shadows.append(shadow)

	vanity = Node2D.new()
	vanity.name = "Vanity"
	add_child(vanity)
	sprite(vanity, room["vanity"]["background"], -10)
	sprite(vanity, room["vanity"]["foreground"], 8)
	var prop: Dictionary = room["vanity"]["lipstick"]
	prop_point = xy(prop["grip_xy"])
	prop_base = xy(prop["base_xy"])
	lipstick_shadow = Shadow.new()
	lipstick_shadow.z_index = -3
	vanity.add_child(lipstick_shadow)
	lipstick = sprite(vanity, prop["texture"], 6)
	lipstick.offset = -xy(prop["grip_pivot_px"])
	lipstick.scale = Vector2.ONE * prop["scale"]


func _process(delta: float) -> void:
	if rendering:
		return
	elapsed += delta
	var frame := int(elapsed * float(timeline["fps"]))
	if frame >= int(timeline["frames"]):
		elapsed = 0.0
		frame = 0
		previous = -1
	if frame != previous:
		apply_frame(frame)
		play_events(previous,frame)
		previous = frame


func prepare_audio() -> void:
	for cue in timeline["events"]:
		var stream: AudioStream
		if cue["audio"] == "raina":
			var source := "res://../../assets/voice/raina_pilot_line.mp3"
			if FileAccess.file_exists(source):
				var voice := AudioStreamMP3.new()
				voice.data = FileAccess.get_file_as_bytes(source)
				stream = voice
		else:
			stream = load("res://audio/" + String(cue["audio"]))
		var player := AudioStreamPlayer.new()
		player.stream = stream
		player.volume_db = linear_to_db(float(cue["gain"]))
		add_child(player)
		preview_audio.append(player)
		if cue["audio"] == "raina":
			audio_on = stream != null


func play_events(earlier: int, current: int) -> void:
	for i in timeline["events"].size():
		var cue: Dictionary = timeline["events"][i]
		if int(cue["frame"]) > earlier and int(cue["frame"]) <= current and preview_audio[i].stream:
			preview_audio[i].play(float(cue["attack_sample"])/48000.0)


func _exit_tree() -> void:
	for player in preview_audio:
		player.stop()
		player.stream = null
	preview_audio.clear()


func write_frames(folder: String, frames: Array) -> void:
	var err := DirAccess.make_dir_recursive_absolute(folder)
	if err != OK:
		push_error("Kare klasörü oluşturulamadı.")
		get_tree().quit(1)
		return
	for frame in frames:
		apply_frame(frame)
		await RenderingServer.frame_post_draw
		var picture := get_viewport().get_texture().get_image()
		if picture == null or picture.get_size() != Vector2i(540,960):
			push_error("Godot viewport 540×960 raster kare döndürmedi.")
			get_tree().quit(1)
			return
		err = picture.save_png(folder.path_join("frame_%04d.png" % frame))
		if err != OK:
			push_error("PNG kare yazılamadı: " + str(frame))
			get_tree().quit(1)
			return
	get_tree().quit()


func apply_frame(frame: int) -> void:
	walk.visible = frame < CUT
	vanity.visible = frame >= CUT
	if frame < CUT:
		walk_frame(frame)
	else:
		vanity_frame(frame)


func ease_between(f: float, a: float, b: float) -> float:
	return smoothstep(a,b,f)


func pulse(f: float, start: float, end: float) -> float:
	var t := clampf((f-start)/(end-start),0,1)
	return pow(sin(t*PI),2)


func foot(f: int, from: Vector2, to: Vector2, start: int, contact: int, height: float) -> Vector2:
	var blend := ease_between(f,start,contact)
	var stride := clampf(float(f-start)/(contact-start),0,1)
	var lift := pow(maxf(0,sin(stride*PI)),1.13)
	return from.lerp(to, blend) - Vector2(0, height*lift)


func shoe_pitch(f: int, start: int, contact: int) -> float:
	return .52*pulse(f,start,contact-5) - .18*ease_between(f,contact-7,contact) + .18*ease_between(f,contact,contact+5)


func walk_frame(f: int) -> void:
	actor.scale = Vector2.ONE * .49
	var far_heel := foot(f,Vector2(119,850),Vector2(222,852),1,18,44)
	var near_heel := foot(f,Vector2(91,860),Vector2(343,860),18,43,61)
	var weight := .42*ease_between(f,2,18) + .58*ease_between(f,20,52)
	var bounce := 7*pulse(f,0,18) + 8*pulse(f,20,43) - 3*pulse(f,43,52)
	var hip_x := 129+164*weight
	var far_pitch := shoe_pitch(f,1,18)
	var near_pitch := shoe_pitch(f,18,43)
	var far_limit := hip_y_limit(hip_x, far_heel, Rig.HIP_FAR, far_pitch)
	var near_limit := hip_y_limit(hip_x, near_heel, Rig.HIP_NEAR, near_pitch)
	actor.position = Vector2(hip_x,maxf(516-bounce,maxf(far_limit,near_limit)))
	var arm_swing := 31*pulse(f,0,20)-39*pulse(f,19,45)
	var lean := -.017+.046*weight+.031*pulse(f,19,44)
	actor.pose_body(lean, actor.to_local(far_heel),actor.to_local(near_heel),
		far_pitch, near_pitch,
		Vector2(-105+arm_swing,43),Vector2(129-arm_swing,39),-.07,0)
	actor.pose_face(.02-.037*pulse(f,7,23)+.048*ease_between(f,45,65),-.9*bounce,
		Vector2(12.5,0)-Vector2(2,0)*ease_between(f,45,65),
		1.0-.9*pulse(f,45,51), Vector2(-1.3,0), .13,0,Vector2.ONE,.049*pulse(f,4,22)-.04*pulse(f,22,47))
	update_shadow(floor_shadows[0],(far_heel+near_heel)*.5+Vector2(15,5),Vector2(77,17),.30)
	update_shadow(floor_shadows[1],Vector2(far_heel.x+13,852),Vector2(34,7),.42-.28*pulse(f,1,18))
	update_shadow(floor_shadows[2],Vector2(near_heel.x+13,860),Vector2(39,8),.50-.33*pulse(f,18,43))


func hip_y_limit(hip_x: float, heel: Vector2, joint: Vector2, pitch: float) -> float:
	var scale_factor := actor.scale.x
	var ankle := heel + Rig.ANKLE_FROM_HEEL.rotated(pitch)*scale_factor
	var span := (Rig.THIGH + Rig.CALF - 5) * scale_factor
	var sideways := ankle.x - hip_x - joint.x * scale_factor
	return ankle.y - joint.y * scale_factor - sqrt(maxf(0, span*span-sideways*sideways))


func update_shadow(item: Shadow, at: Vector2, radius: Vector2, strength: float) -> void:
	item.position = at
	item.radii = radius
	item.strength = strength
	item.queue_redraw()


func mouth_at(f: int) -> Vector3:
	if not audio_on:
		return VOWELS["rest"]
	var time := (f - int(dialogue["start_frame"])) / float(timeline["fps"])
	var cues: Array = dialogue["visemes"]
	if time < 0:
		return VOWELS["rest"]
	for i in range(1,cues.size()):
		var next: Array = cues[i]
		if time <= float(next[0]):
			var earlier: Array = cues[i-1]
			var shape: Vector3 = VOWELS[earlier[1]]
			return shape.lerp(VOWELS[next[1]],ease_between(time,earlier[0],next[0]))
	return VOWELS["rest"]


func vanity_frame(f: int) -> void:
	actor.scale = Vector2.ONE * 1.13
	var forward := ease_between(f,82,108) - ease_between(f,120,149)
	var recover := ease_between(f,274,291)
	var listen := pulse(f,132,158)
	var turn := ease_between(f,126,151)
	var thought := pulse(f,133,154)
	var chuckle_range: Array = dialogue["chuckle"]
	var chuckle := pulse(f,int(chuckle_range[0]*30)+156,int(chuckle_range[1]*30)+156) if audio_on else 0.0
	var breath := pulse(f,70,110)*2.0 + pulse(f,144,158)*2.8
	var shake := 2.5*chuckle + 1.5*pulse(f,223,241)
	actor.position = Vector2(177+forward*8+recover*2, 817-breath-shake)
	var lean := -.065 + forward*.14 + .032*turn + .017*pulse(f,175,192) - .035*pulse(f,222,244)
	var turn_in_hand := .17*ease_between(f,LIFT,141) -.12*pulse(f,208,241)
	turn_in_hand *= 1.0-ease_between(f,268,PLACE)
	var angle := -1.49 + turn_in_hand
	var held := f >= GRAB and f <= PLACE
	var pinch := ease_between(f,106,GRAB) * (1.0-ease_between(f,RELEASE,290))
	var object_target := prop_point.lerp(Vector2(395,547),ease_between(f,LIFT,140))
	object_target += Vector2(-9*pulse(f,176,205) + 10*pulse(f,215,244), -14*pulse(f,212,247)-4*chuckle)
	var lowering := clampf((f-268.0)/(PLACE-268),0,1)
	object_target.x = lerpf(object_target.x, prop_point.x, smoothstep(0,1,lowering))
	object_target.y = lerpf(object_target.y, prop_point.y, pow(lowering,1.25))
	var wrist_around_prop := object_target - Rig.GRIP.rotated(angle) * actor.scale.x
	var rest := actor.to_global(Vector2(135,30))
	var approach := ease_between(f,82,GRAB)
	var retreat := ease_between(f,RELEASE,300)
	var near_target := wrist_around_prop + Vector2(-22,34)*pulse(f,82,GRAB)
	var wrist := rest.lerp(near_target,approach*(1.0-retreat))
	var hand_turn := lerpf(-.10,angle,approach*(1.0-retreat))
	actor.pose_body(lean,Vector2(-74,650),Vector2(64,650),0,0,
		Vector2(-114,40 - 9*chuckle),actor.to_local(wrist),hand_turn,pinch)

	lipstick.position = object_target if held else prop_point
	lipstick.rotation = turn_in_hand if held else 0.0
	var rise := maxf(0,prop_point.y - lipstick.position.y)
	update_shadow(lipstick_shadow,prop_base + Vector2(-rise*.13,1),
		Vector2(14+rise*.21,2.5+rise*.044),.31/(1+rise*.075))

	var lids := 1.0 - .94*pulse(f,74,80) - .94*pulse(f,144,151) - .84*pulse(f,206,212) - .77*chuckle
	lids -= .18*thought + .15*pulse(f,219,246)
	var gaze := Vector2(9.5,.8) + Vector2(3,1.9)*forward - Vector2(0,5.5)*turn - Vector2(3.0,3.0)*thought
	gaze += Vector2(1.3,7)*recover
	var brow_stroke := -10*listen-5*pulse(f,166,185)-4.8*pulse(f,223,242)
	var mouth_pose := mouth_at(f)
	actor.pose_face(-.035+forward*.08+listen*.105-.10*pulse(f,221,246)+.05*chuckle,
		-shake*1.6,gaze,lids,Vector2(brow_stroke,-2*thought-3*pulse(f,222,239)),
		.20+.51*chuckle+.22*pulse(f,220,270),mouth_pose.x,Vector2(mouth_pose.y,mouth_pose.z),
		.027*pulse(f,84,116)-.021*pulse(f,122,161)+.033*chuckle)
