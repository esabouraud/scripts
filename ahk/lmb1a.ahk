; lmb1a.ahk
;
; When right mouse button is held, holding left mouse button emulates
; pressing "1" key once and repeatedly then at a random interval between
; 231 and 517 milliseconds
~RButton & LButton::
	While GetKeyState("LButton","P") {
		Send 1
		Random, rand, 231, 517
		Sleep rand
	}
return
