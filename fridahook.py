from subprocess import check_output
import frida
import os

class FridaHook():
	def __init__(self):
		self.session = None

		try:
			self.session = frida.attach("PwnAdventure3-Win32-Shipping.exe")
		except Exception as p:
			print("ERROR: Multiple PwnAdventure3 instances detected!")
			print(p)
			print("Please input a PID to attach to:")
			PID = int(input("PID: "))
			self.session = frida.attach(PID)
		
		script = self.session.create_script("""
			console.log("");
			console.log("-- PwnAdventure3 Frida Hack --");
			console.log("");

			var GameLogicBase = Module.findBaseAddress("GameLogic.dll");
			console.log("[!] GameLogicBase: " + GameLogicBase);

			var GameLogicPlayer;

			var offsets = {
				"Actor::GetPosition()": 0x16f0,
				"Actor::SetPosition()": 0x1c80,
				"ClientWorld::Tick()": 0xcae0,
				"Player": {
					"walkingSpeed": 0x120,
					"jumpSpeed": 0x124,
					"mana": 0xbc
				},
				"Player::Chat()": 0x551a0,
				"Player::GetMana()": 0x4ff70,
				"Player::GetWalkingSpeed()": 0x4ff90,
				"Player::GetJumpSpeed()": 0x4ffa0,
				"GameAPI::GetGoldenEggList()": 0x1e3c0,
				"GameAPI::Log()": 0x1e790,
				"GameAPI::GetAchievement()": 0x1df90,
			};

			var cheats = {
				speed: {
					enabled: false,
					value: 200
				},
				jump: {
					enabled: false,
					value: 200
				},
				freeze: {
					enabled: false,
					position: null
				}
			};

			var GetPosition = ptr(GameLogicBase).add(offsets["Actor::GetPosition()"]);
			console.log("[!] Actor::GetPosition(): " + GetPosition);

			var SetPosition = ptr(GameLogicBase).add(offsets["Actor::SetPosition()"]);
			console.log("[!] Actor::SetPosition(): " + SetPosition);

			var fnGetPosition = new NativeFunction(GetPosition, 'pointer', ['pointer', 'pointer', 'pointer'], 'fastcall');
			var fnSetPosition = new NativeFunction(SetPosition, 'void', ['pointer', 'pointer', 'pointer'], 'fastcall');

			var ClientTick = ptr(GameLogicBase).add(offsets["ClientWorld::Tick()"]);
			console.log("[!] ClientWorld::Tick(): " + ClientTick);

			var PlayerChat = ptr(GameLogicBase).add(offsets["Player::Chat()"]);
			console.log("[!] Player::Chat(): " + PlayerChat);

			var WalkingSpeed = ptr(GameLogicBase).add(offsets["Player::GetWalkingSpeed()"]);
			console.log("[!] Player::GetWalkingSpeed(): " + WalkingSpeed);

			var JumpSpeed = ptr(GameLogicBase).add(offsets["Player::GetWalkingSpeed()"]);
			console.log("[!] Player::GetWalkingSpeed(): " + WalkingSpeed);

			var PlayerMana = ptr(GameLogicBase).add(offsets["Player::GetMana()"]);
			console.log("[!] Player::GetMana(): " + PlayerMana);

			var GetGoldenEggList = ptr(GameLogicBase).add(offsets["GameAPI::GetGoldenEggList()"]);
			console.log("[!] GameAPI::GetGoldenEggList(): " + GetGoldenEggList);
			var fnGetGoldenEggList = new NativeFunction(GetGoldenEggList, 'pointer', ['pointer'], 'fastcall');

			var Log = ptr(GameLogicBase).add(offsets["GameAPI::Log()"]);
			console.log("[!] GameAPI::Log(): " + Log);

			var GetAchievement = ptr(GameLogicBase).add(offsets["GameAPI::GetAchievement()"]);
			console.log("[!] GameAPI::GetAchievement(): " + GetAchievement);
			var fnGetAchievement = new NativeFunction(GetAchievement, 'void', ['pointer'], 'fastcall');

			Interceptor.attach(PlayerChat, {
				onEnter: function(args) {
					var msg = Memory.readCString(args[0]);

					console.log("[Chat]: " + msg);

					if(msg.trim().startsWith(".")) {
						var cmd = msg.trim().slice(1);

						if(cmd == "solve") {
							send({
								type: "circuit",
								bits: "01101001100011111010101111111010"
							});
						}

						if(cmd == "test") {
							var name = Memory.allocUtf8String("RightToArmBears");
							fnGetAchievement(name);

							console.log("RightToArmBears");
						}

						if(cmd.startsWith("bits")) {
							var bits = cmd.split(" ")[1] || "00000000000000000000000000000000";

							send({
								type: "circuit",
								bits: bits
							});
						}

						if(cmd == "brute") {
							send({
								type: "brute"
							});
						}

						if(cmd.startsWith("setspeed ")) {
							var speed = cmd.replace("setspeed ", "");

							if(speed == "default") {
								cheats.speed = {
									enabled: true,
									value: 200
								}
								
								send({
									"type": "banner",
									"top": "~~ SpeedHack ~~",
									"bottom": "SpeedHack disabled."
								})
							}
							else {
								cheats.speed = {
									enabled: true,
									value: parseFloat(speed)
								}

								send({
									"type": "banner",
									"top": "~~ SpeedHack ~~",
									"bottom": "SpeedHack enabled: " + speed + " speed."
								});
							}
						}

						if(cmd.startsWith("setjump ")) {
							var jump = cmd.replace("setjump ", "");

							if(jump == "default") {
								cheats.jump = {
									enabled: true,
									value: 420
								}
								
								send({
									"type": "banner",
									"top": "~~ JumpHack ~~",
									"bottom": "JumpHack disabled."
								})
							}
							else {
								cheats.jump = {
									enabled: true,
									value: parseFloat(jump)
								}

								send({
									"type": "banner",
									"top": "~~ JumpHack ~~",
									"bottom": "JumpHack enabled: " + jump + " jump."
								});
							}
						}

						if(cmd.startsWith("pos") || cmd.startsWith("coord")) {
							var vecPos = Memory.alloc(12);
							fnGetPosition(GameLogicPlayer, vecPos, vecPos);

							var x = Memory.readFloat(vecPos),
								y = Memory.readFloat(ptr(vecPos).add(4)),
								z = Memory.readFloat(ptr(vecPos).add(8));

							console.log("[!] Position: " + [x, y, z].join(" "));

							var pos = [parseInt(x), parseInt(y), parseInt(z)];

							send({
								"type": "banner",
								"top": "~~ Position ~~",
								"bottom": pos.join(" ")
							});
						}

						if(cmd.startsWith("tp ")) {
							var keyword = cmd.replace("tp ", "").toLowerCase();
							var pos = keyword.split(" ");
							var vecPos = Memory.alloc(12);

							if(pos.length == 3) {
								Memory.writeFloat(vecPos, 				parseFloat(pos[0]));
								Memory.writeFloat(ptr(vecPos).add(4), 	parseFloat(pos[1]));
								Memory.writeFloat(ptr(vecPos).add(8), 	parseFloat(pos[2]));
							}
							else if(pos.length == 1) {
								if(keyword == "blocky") {
									Memory.writeFloat(vecPos, 				-19677);
									Memory.writeFloat(ptr(vecPos).add(4), 	-4271);
									Memory.writeFloat(ptr(vecPos).add(8), 	2272);
								}
								else if(keyword == "blocky_final") {
									Memory.writeFloat(vecPos, 				-3231);
									Memory.writeFloat(ptr(vecPos).add(4), 	-3999);
									Memory.writeFloat(ptr(vecPos).add(8), 	2273);
								}
								else {
									return;
								}
							}
							else {
								return;
							}

							fnSetPosition(GameLogicPlayer, vecPos, vecPos);

							send({
								"type": "banner",
								"top": "~~ TeleportHack ~~",
								"bottom": "Teleported."
							});

							console.log("[!] Teleported to: " + pos.join(", "));
						}

						if(cmd.startsWith("freeze ")) {
							var keyword = cmd.replace("freeze ", "");
							if(keyword == "off" || keyword.startsWith("disable")) {
								cheats.freeze = {
									enabled: false,
									position: null
								};

								send({
									"type": "banner",
									"top": "~~ FreezeHack ~~",
									"bottom": "FreezeHack disabled."
								});
							}
							else {
								var args = cmd.replace("freeze ", "").split(" ");
								var vecPos = Memory.alloc(12);
								var pos = [];

								if(args.length == 3) {
									Memory.writeFloat(vecPos, 				parseFloat(args[0]));
									Memory.writeFloat(ptr(vecPos).add(4), 	parseFloat(args[1]));
									Memory.writeFloat(ptr(vecPos).add(8), 	parseFloat(args[2]));

									pos = [parseFloat(args[0]), parseFloat(args[1]), parseFloat(args[2])];
								}
								else {
									fnGetPosition(GameLogicPlayer, vecPos, vecPos);

									pos = [
										Memory.readFloat(vecPos),
										Memory.readFloat(ptr(vecPos).add(4)),
										Memory.readFloat(ptr(vecPos).add(8))
									]
								}

								fnSetPosition(GameLogicPlayer, vecPos, vecPos);

								cheats.freeze = {
									enabled: true,
									position: pos
								}

								send({
									"type": "banner",
									"top": "~~ FreezeHack ~~",
									"bottom": "You are now frozen!"
								});

								console.log("[!] Frozen at: " + pos.join(", "));
							}
						}

						if(cmd.startsWith("egg")) {
							var eggsPointer = Memory.alloc(8);
							eggsPointer = fnGetGoldenEggList(this.context);

							console.log(eggsPointer);
						}
					}
				}
			});

			Interceptor.attach(WalkingSpeed, {
				onEnter: function(args) {
					var Player = this.context.ecx;
					GameLogicPlayer = ptr(Player).sub(0x70);
				},
				onLeave: function(args) {
					if(cheats.speed.enabled) {
						var Player = this.context.ecx;
						Memory.writeFloat(ptr(Player).add(offsets["Player"]["walkingSpeed"]), cheats.speed.value);
					}
				}
			});

			Interceptor.attach(JumpSpeed, {
				onEnter: function(args) {
					var Player = this.context.ecx;
					//console.log(Memory.readFloat(ptr(Player).add(offsets["Player"]["jumpSpeed"])));
				},
				onLeave: function(args) {
					if(cheats.jump.enabled) {
						var Player = this.context.ecx;
						Memory.writeFloat(ptr(Player).add(offsets["Player"]["jumpSpeed"]), cheats.jump.value);
					}
				}
			});

			Interceptor.attach(PlayerMana, {
				onEnter: function(args) {
					var Player = this.context.ecx;
					//console.log("[PlayerMana]: " + Memory.readInt(ptr(Player).add(offsets["Player"]["mana"])));
				},
				onLeave: function(args) {
					var Player = this.context.ecx;
					//Memory.writeInt(ptr(Player).add(offsets["Player"]["mana"]), 500);
					// ^ stored server side, probably same as health
				}
			});

			Interceptor.attach(ClientTick, {
				onLeave: function(args) {
					if(cheats.freeze.enabled) {
						var vecPos = Memory.alloc(12);
						Memory.writeFloat(vecPos, 				cheats.freeze.position[0]);
						Memory.writeFloat(ptr(vecPos).add(4), 	cheats.freeze.position[1]);
						Memory.writeFloat(ptr(vecPos).add(8), 	cheats.freeze.position[2]);
						fnSetPosition(GameLogicPlayer, vecPos, vecPos);
					}
				}
			});

			function parseFmtString(fmt, args, start) {
				start = start || 2;

			    var chunks = fmt.split(/%./);
			    var modifiers = fmt.match(/%./g);
			    var msg = "";

			    if(chunks.length == 1)
			    	return fmt;

			    for(var i = 0; i < chunks.length; i++) {
			        msg += chunks[i];

			        if(!modifiers[i])
			        	continue;

			        if(modifiers[i] == "%s") {
			            msg += Memory.readCString(args[start]);
			        }
			        else if(modifiers[i] == "%d") {
			            msg += parseInt(args[start], 16);
			        }
			        else if(modifiers[i] == "%f") {
			            msg += parseFloat(args[start], 16);
			        }
			        else {
			        	msg += modifiers[i];
			        }

			        start++;
			    }
			    return msg;
			}

			Interceptor.attach(Log, {
				onEnter: function(args) {
					var msg = Memory.readCString(args[1]);
					console.log("[Log] " + parseFmtString(msg, args));
				}	
			});
		""");

		self.utils = None

		def on_message(message, data):
			if "payload" not in message:
				print(message, data)
				return

			payload = message["payload"]
			if payload["type"] == "banner":
				self.utils.banner(payload["top"], payload["bottom"])
			elif payload["type"] == "circuit":
				self.utils.circuit(payload["bits"])
			elif payload["type"] == "brute":
				for check in range(37660, 0xFFFF+1):
					bCheck = bin(check)[2:].zfill(16)
					bits = "".join(i + j for i, j in zip("0_1_1_0_1_0_1_1_1_1_1_1_1_1_1_1_".replace('_',''), bCheck))

					self.utils.circuit(bits)

		script.on('message', on_message)
		script.load()

		print("[!] FridaHook activated!")

	def unload(self):
		self.session.detach()
		pass