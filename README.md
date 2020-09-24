# PwnAdventure3

My game hack / network proxy / keygen for PwnAdventure3: Pwnie Island.

The core parts of this repository are the Frida hook which injects directly into the PwnAdventure3 process, and the network proxy which sits in between the client and the game server.

The Frida hook can solve the blocky's revenge circuit, hook into chat, teleport players, set walking/jumping speed, freeze the current position, and more.

The network proxy allows for real time inspection and modification of the game packets, and allows the injection of new packets like the banner packet used to display hack messages to the client.
