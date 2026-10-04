KEYBOARD    = $0200
DISPLAY     = $0400
DISK_CMD    = $0320
DISK_SEC    = $0321
DISK_BUFL   = $0322
DISK_BUFH   = $0323
PROG_ADDR   = $2000
GAME_ADDR   = $2100 ;G loads disk sectors 2-5 here and runs it

CUR_L       = $10 ;screen cursor pointer (16 bit)
CUR_H       = $11
COL         = $12 ;column 0-39
TMP         = $13 ;saved Y during putchar
LEN         = $14 ;characters typed on this line
CMDCH       = $15 ;first character typed on this line
SRC_L       = $16 ;scroll copy pointers
SRC_H       = $17
DST_L       = $18
DST_H       = $19
SECN        = $1A ;sector counter for G
PAGEH       = $1B ;load page for G

    .ORG $8000

RESET:
    SEI
    CLD
    LDX #$FF
    TXS
    JSR SYS_CLEAR
    LDA #$00
    STA CUR_L
    STA COL
    LDA #$04
    STA CUR_H
    JMP SHELL_PROMPT

BRK_HANDLER: ;a program that hits BRK ends up back at the shell
    LDX #$FF
    TXS
    JMP SHELL_PROMPT

SYS_CLEAR: ;fills the screen with spaces
    LDX #$00
    LDA #$20

CLEAR_LOOP:
    STA $0400,X
    STA $0500,X
    STA $0600,X
    STA $0700,X
    INX
    BNE CLEAR_LOOP
    RTS

SYS_GETCHAR: ;waits for a key, returns it in A
    LDA KEYBOARD
    BEQ SYS_GETCHAR
    RTS

SYS_PUTCHAR: ;prints A at the cursor. handles enter ($0D) and backspace ($08). keeps Y
    STY TMP
    CMP #$0D
    BEQ PC_ENTER
    CMP #$08
    BEQ PC_BKSP
    LDY #$00
    STA (CUR_L),Y
    JSR CUR_INC
    JMP PC_DONE

PC_ENTER:
    JSR NEWLINE
    JMP PC_DONE

PC_BKSP: ;move the cursor back one cell and blank it
    LDA CUR_L
    BNE PB_1
    DEC CUR_H
PB_1:
    DEC CUR_L
    LDA COL
    BNE PB_2
    LDA #$28
    STA COL
PB_2:
    DEC COL
    LDA #$20
    LDY #$00
    STA (CUR_L),Y

PC_DONE:
    LDY TMP
    RTS

CUR_INC: ;moves the cursor forward one cell, scrolls at the bottom
    INC CUR_L
    BNE CI_1
    INC CUR_H
CI_1:
    INC COL
    LDA COL
    CMP #$28
    BNE CI_2
    LDA #$00
    STA COL
CI_2:
    LDA CUR_H
    CMP #$07
    BNE CI_DONE
    LDA CUR_L
    CMP #$E8
    BCC CI_DONE
    JSR SCROLL
    LDA #$C0
    STA CUR_L
    LDA #$07
    STA CUR_H
    LDA #$00
    STA COL
CI_DONE:
    RTS

NEWLINE: ;moves the cursor to the start of the next row
    JSR CUR_INC
    LDA COL
    BNE NEWLINE
    RTS

SCROLL: ;moves rows 1-24 up to rows 0-23 and blanks the last row
    LDA #$00
    STA DST_L
    LDA #$04
    STA DST_H
    LDA #$28
    STA SRC_L
    LDA #$04
    STA SRC_H
    LDX #$03
SC_PAGE:
    LDY #$00
SC_BYTE:
    LDA (SRC_L),Y
    STA (DST_L),Y
    INY
    BNE SC_BYTE
    INC SRC_H
    INC DST_H
    DEX
    BNE SC_PAGE
    LDY #$00
SC_REST:
    LDA (SRC_L),Y
    STA (DST_L),Y
    INY
    CPY #$C0
    BNE SC_REST
    LDA #$20
    LDY #$00
SC_CLR:
    STA $07C0,Y
    INY
    CPY #$28
    BNE SC_CLR
    RTS

PRINT_OK:
    LDA #$4F
    JSR SYS_PUTCHAR
    LDA #$4B
    JSR SYS_PUTCHAR
    LDA #$0D
    JSR SYS_PUTCHAR
    RTS

SHELL_PROMPT:
    LDA COL
    BEQ SP_GO
    LDA #$0D
    JSR SYS_PUTCHAR
SP_GO:
    LDA #$00
    STA LEN
    LDA #$3E
    JSR SYS_PUTCHAR

SHELL_LOOP:
    JSR SYS_GETCHAR
    CMP #$0D
    BEQ SH_ENTER
    CMP #$08
    BEQ SH_BKSP
    CMP #$20
    BCC SHELL_LOOP
    LDX LEN
    CPX #$F0
    BCS SHELL_LOOP
    CPX #$00
    BNE SH_KEEP
    STA CMDCH
SH_KEEP:
    INC LEN
    JSR SYS_PUTCHAR
    JMP SHELL_LOOP

SH_BKSP:
    LDA LEN
    BEQ SHELL_LOOP
    DEC LEN
    LDA #$08
    JSR SYS_PUTCHAR
    JMP SHELL_LOOP

SH_ENTER: ;a command is one letter followed by enter: E R S or L
    LDA #$0D
    JSR SYS_PUTCHAR
    LDA LEN
    CMP #$01
    BNE SH_NONE
    LDA CMDCH
    CMP #$45
    BEQ CMD_EDIT
    CMP #$52
    BEQ CMD_RUN
    CMP #$53
    BEQ CMD_SAVE
    CMP #$4C
    BEQ CMD_LOAD
    CMP #$47
    BEQ CMD_GAME
SH_NONE:
    JMP SHELL_PROMPT
    ;E enter = type text into the buffer at $2000 (Esc to finish)
    ;R enter = run whatever is at $2000
    ;S enter = save $2000 to disk sector 1
    ;L enter = load disk sector 1 to $2000
    ;G enter = load the game from disk sectors 2-5 and play it

CMD_RUN:
    JSR PROG_ADDR
    JMP SHELL_PROMPT

CMD_EDIT:
    LDY #$00

EDIT_LOOP:
    JSR SYS_GETCHAR
    CMP #$1B
    BEQ EDIT_EXIT
    CMP #$08
    BEQ ED_BKSP
    CMP #$0D
    BEQ ED_STORE
    CMP #$20
    BCC EDIT_LOOP
ED_STORE:
    STA PROG_ADDR,Y
    JSR SYS_PUTCHAR
    INY
    BEQ EDIT_FULL
    JMP EDIT_LOOP

ED_BKSP:
    CPY #$00
    BEQ EDIT_LOOP
    DEY
    LDA PROG_ADDR,Y
    CMP #$0D
    BEQ ED_NOBACK
    LDA #$08
    JSR SYS_PUTCHAR
    JMP EDIT_LOOP
ED_NOBACK:
    INY
    JMP EDIT_LOOP

EDIT_EXIT:
    LDA #$00
    STA PROG_ADDR,Y
EDIT_FULL:
    JMP SHELL_PROMPT

CMD_SAVE:
    LDA #$00
    STA DISK_BUFL
    LDA #$20
    STA DISK_BUFH
    LDA #$01
    STA DISK_SEC
    LDA #$02
    STA DISK_CMD
    JSR PRINT_OK
    JMP SHELL_PROMPT

CMD_LOAD:
    LDA #$00
    STA DISK_BUFL
    LDA #$20
    STA DISK_BUFH
    LDA #$01
    STA DISK_SEC
    LDA #$01
    STA DISK_CMD
    JSR PRINT_OK
    JMP SHELL_PROMPT

CMD_GAME: ;loads sectors 2,3,4,5 to $2100-$24FF then runs $2100
    LDA #$02
    STA SECN
    LDA #$21
    STA PAGEH
    LDA #$00
    STA DISK_BUFL
GM_LOOP:
    LDA PAGEH
    STA DISK_BUFH
    LDA SECN
    STA DISK_SEC
    LDA #$01
    STA DISK_CMD
    INC PAGEH
    INC SECN
    LDA SECN
    CMP #$06
    BNE GM_LOOP
    JSR GAME_ADDR
    JSR SYS_CLEAR
    LDA #$00
    STA CUR_L
    STA COL
    LDA #$04
    STA CUR_H
    JMP SHELL_PROMPT
