P1_Y     = $30
P2_Y     = $31
BALL_X   = $32
BALL_Y   = $33
BALL_DX  = $34
BALL_DY  = $35
P1_SCORE = $36
P2_SCORE = $37
TIMER    = $38
PTR_L    = $39
PTR_H    = $3A
SAVESP   = $3B

KEYSTAT  = $0201
KEYDATA  = $0200
ROWL     = $3200
ROWH     = $3300

    .ORG $2100

START:
    TSX
    STX SAVESP
    JSR INIT_ROWS
RESET_GAME:
    JSR CLEAR_SCREEN
    LDA #$0A
    STA P1_Y
    STA P2_Y
    LDA #$14
    STA BALL_X
    LDA #$0C
    STA BALL_Y
    LDA #$01
    STA BALL_DX
    STA BALL_DY
    LDA #$00
    STA P1_SCORE
    STA P2_SCORE
    JSR DRAW_PADDLES

MAIN_LOOP:
    JSR ERASE_BALL
    JSR MOVE_BALL
    JSR DRAW_BALL
    JSR DRAW_PADDLES
    JSR PRINT_SCORES

    LDA #$08
    STA TIMER
DELAY:
    JSR PROCESS_KEYS
    LDX #$FF
D_INNER:
    DEX
    BNE D_INNER
    DEC TIMER
    BNE DELAY
    JMP MAIN_LOOP

PROCESS_KEYS:
    LDA KEYSTAT
    BEQ PK_DONE
    LDA KEYDATA
    CMP #$51
    BEQ QUIT
    CMP #$57
    BEQ P1_UP
    CMP #$53
    BEQ P1_DOWN
    CMP #$49
    BEQ P2_UP
    CMP #$4B
    BEQ P2_DOWN
    JMP PROCESS_KEYS
    ;controls - player 1 uses W and S player 2 uses I and K for up and down respectively

P1_UP:
    LDA P1_Y
    CMP #$01
    BEQ PK_DONE
    DEC P1_Y
    JMP PK_DONE
P1_DOWN:
    LDA P1_Y
    CMP #$14
    BEQ PK_DONE
    INC P1_Y
    JMP PK_DONE
P2_UP:
    LDA P2_Y
    CMP #$01
    BEQ PK_DONE
    DEC P2_Y
    JMP PK_DONE
P2_DOWN:
    LDA P2_Y
    CMP #$14
    BEQ PK_DONE
    INC P2_Y
PK_DONE:
    RTS

QUIT:
    LDX SAVESP
    TXS
    RTS

MOVE_BALL:
    LDA BALL_DY
    BEQ BALL_Y_DN
    DEC BALL_Y
    LDA BALL_Y
    CMP #$01
    BNE CHECK_X
    LDA #$00
    STA BALL_DY
    JMP CHECK_X
BALL_Y_DN:
    INC BALL_Y
    LDA BALL_Y
    CMP #$17
    BNE CHECK_X
    LDA #$01
    STA BALL_DY

CHECK_X:
    LDA BALL_DX
    BEQ BALL_X_R
    DEC BALL_X
    LDA BALL_X
    CMP #$02
    BNE MB_DONE
    LDA BALL_Y
    SEC
    SBC P1_Y
    BCC P2_SCORED
    CMP #$04
    BCS P2_SCORED
    LDA #$00
    STA BALL_DX
    RTS

BALL_X_R:
    ; Moving Right
    INC BALL_X
    LDA BALL_X
    CMP #$25
    BNE MB_DONE
    LDA BALL_Y
    SEC
    SBC P2_Y
    BCC P1_SCORED
    CMP #$04
    BCS P1_SCORED
    LDA #$01
    STA BALL_DX
MB_DONE:
    RTS

P1_SCORED:
    INC P1_SCORE
    JMP RESET_BALL
P2_SCORED:
    INC P2_SCORE
RESET_BALL:
    JSR ERASE_BALL
    LDA #$14
    STA BALL_X
    LDA #$0C
    STA BALL_Y
    RTS

INIT_ROWS:
    LDA #$00
    STA PTR_L
    LDA #$04
    STA PTR_H
    LDX #$00
IR_LOOP:
    LDA PTR_L
    STA ROWL,X
    LDA PTR_H
    STA ROWH,X
    CLC
    LDA PTR_L
    ADC #$28
    STA PTR_L
    BCC IR_NC
    INC PTR_H
IR_NC:
    INX
    CPX #$19
    BNE IR_LOOP
    RTS

CLEAR_SCREEN:
    LDX #$00
    LDA #$20
CS_LOOP:
    STA $0400,X
    STA $0500,X
    STA $0600,X
    STA $0700,X
    INX
    BNE CS_LOOP
    RTS

DRAW_PADDLES:
    LDX #$01
CP_L:
    LDA ROWL,X
    STA PTR_L
    LDA ROWH,X
    STA PTR_H
    LDA #$20
    LDY #$01
    STA (PTR_L),Y
    LDY #$26
    STA (PTR_L),Y
    INX
    CPX #$18
    BNE CP_L
    LDX P1_Y
    LDY #$00
DP1:
    LDA ROWL,X
    STA PTR_L
    LDA ROWH,X
    STA PTR_H
    LDA #$7C
    STY $3F
    LDY #$01
    STA (PTR_L),Y
    LDY $3F
    INX
    INY
    CPY #$04
    BNE DP1
    LDX P2_Y
    LDY #$00
DP2:
    LDA ROWL,X
    STA PTR_L
    LDA ROWH,X
    STA PTR_H
    LDA #$7C
    STY $3F
    LDY #$26
    STA (PTR_L),Y
    LDY $3F
    INX
    INY
    CPY #$04
    BNE DP2
    RTS

DRAW_BALL:
    LDX BALL_Y
    LDA ROWL,X
    STA PTR_L
    LDA ROWH,X
    STA PTR_H
    LDY BALL_X
    LDA #$4F ; 'O'
    STA (PTR_L),Y
    RTS

ERASE_BALL:
    LDX BALL_Y
    LDA ROWL,X
    STA PTR_L
    LDA ROWH,X
    STA PTR_H
    LDY BALL_X
    LDA #$20
    STA (PTR_L),Y
    RTS

PRINT_SCORES:
    LDA P1_SCORE
    CLC
    ADC #$30
    STA $0408
    LDA P2_SCORE
    CLC
    ADC #$30
    STA $041F
    RTS
