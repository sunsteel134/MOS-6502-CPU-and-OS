KEYBOARD    = $0200
DISPLAY     = $0400
DISK_CMD    = $0320
DISK_SEC    = $0321
DISK_BUFL   = $0322
DISK_BUFH   = $0323
PROG_ADDR   = $0500

    .ORG $8000

RESET:
    SEI
    CLD
    LDX #$FF
    TXS
    JSR SYS_CLEAR
    JMP SHELL_START

SYS_CLEAR: ;clears whats loaded right now
    LDX #$00
    LDA #$20

CLEAR_LOOP: ;clears everything
    STA $0400,X
    STA $0500,X
    STA $0600,X
    STA $0700,X
    INX
    BNE CLEAR_LOOP
    RTS

SYS_GETCHAR: ;gets the character youve pressed
    LDA KEYBOARD
    BEQ SYS_GETCHAR
    PHA
    LDA #$00
    STA KEYBOARD
    PLA
    RTS

SYS_PUTCHAR: ;dislays a character
    STA DISPLAY,X
    INX
    RTS

SHELL_START: ;starts the shell
    LDA #$3E
    JSR SYS_PUTCHAR

SHELL_LOOP: ;loop for the doing of stuff
    JSR SYS_GETCHAR
    CMP #$45
    BEQ CMD_EDIT
    CMP #$52
    BEQ CMD_RUN
    CMP #$53
    BEQ CMD_SAVE
    CMP #$4C
    BEQ CMD_LOAD
    JSR SYS_PUTCHAR
    JMP SHELL_LOOP
    ;L means load disk sector 1 to $0500
    ;S means save $0500 to disk sector 1
    ;R means run
    ;E means write code

CMD_RUN: ;run program
    JSR PROG_ADDR
    JMP SHELL_START

CMD_EDIT: ;writes asssembly
    LDY #$00

EDIT_LOOP: ;lets you edit things
    JSR SYS_GETCHAR
    CMP #$1B
    BEQ EDIT_EXIT
    STA $0500,Y
    JSR SYS_PUTCHAR
    INY
    JMP EDIT_LOOP

EDIT_EXIT: ;stop editting
    JMP SHELL_START

CMD_SAVE: ;save to disk
    LDA #$00
    STA DISK_BUFL
    LDA #$05
    STA DISK_BUFH
    LDA #$01
    STA DISK_SEC
    LDA #$02
    STA DISK_CMD
    JMP SHELL_START

CMD_LOAD: ;load from disk
    LDA #$00
    STA DISK_BUFL
    LDA #$05
    STA DISK_BUFH
    LDA #$01
    STA DISK_SEC
    LDA #$01
    STA DISK_CMD
    JMP SHELL_START
