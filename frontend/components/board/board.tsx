'use client'

import {flushSync} from "react-dom"
import Squares from "./board-elements/squares/squares"
import {useState, useEffect, useRef} from "react";
import NewGamePanel from "./board-elements/new-game-panel/new-game-panel";
import PromotionPanel from "./board-elements/promotion-panel/promotion-panel";
import { useChessGame } from "@/contexts/ChessGameContext";

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
console.log('API_URL:', API_URL);
console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);

export default function Board(){
    const { gamefinished, setGameFinished, winner, setWinner, setMovesHistory, board, setBoard, boardHistory, setBoardHistory, setAiScore, selectedSquareStart, setSelectedSquareStart, validEndSquares, setValidEndSquares } = useChessGame();

    const playSound = (soundPath: string) => {
        const audio = new Audio(soundPath);
        audio.play();
    };
    const [turnWhite, setTurnWhite] = useState(true);
    const [humanIsWhite, setHumanIsWhite] = useState<boolean | null>(true);
    const [promotionPanelOpen, setPromotionPanelOpen] = useState(false);
    const [promotion, setPromotion] = useState(false);
    const [pendingEndpos, setPendingEndpos] = useState<number[] | null>(null);

    function startNewGame(color: string): void{
        flushSync(() => setHumanIsWhite(null));

        if (color === 'white') {
            setHumanIsWhite(true);
        } else if (color === 'black') {
            setHumanIsWhite(false);
        } else {
            setHumanIsWhite(Math.random() > 0.5);
        }

        setTurnWhite(true);
        setGameFinished(false);
        setWinner(null);
    }

    const syncGameState = async () => {
        const response = await fetch(`${API_URL}/game-state?human_is_white=${humanIsWhite}&reset_game=true`);
        const data = await response.json();
        setBoard(data.board_history[data.board_history.length - 1]);
        setBoardHistory(data.board_history);
        setMovesHistory(data.moves_history);
        setAiScore(0.00);

        if (!humanIsWhite) {
            letAIMove();
        }
    };

    useEffect(() => {
        if (humanIsWhite !== null) {
            syncGameState();
        }
    }, [humanIsWhite]);


    const makeMove = async (startpos: number[], endpos: number[], promotion_piece: string | null = null) => {
        const response = await fetch("${API_URL}/make-move", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({startpos: startpos, endpos: endpos, promotion_piece: promotion_piece})
        });
        const data = await response.json();

        setBoard(data.board_history[data.board_history.length - 1]);
        setBoardHistory(data.board_history);
        setTurnWhite(prev => !prev);
        setMovesHistory(data.moves_history);

        const soundToPlay = data.is_capture ? '/move_capture.mp3' : '/move_from_human.mp3';
        playSound(soundToPlay);

        if (data.gameStatus.gameIsFinished) {
            setGameFinished(true);
            setWinner(data.gameStatus.winner);
        }

        return {success: true, gameStatus: data.gameStatus};

    }

    const showValidEndSquares = async (startpos: number[]) => {
        const response = await fetch("${API_URL}/valid-end-squares", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({startpos: startpos})
        })
        const data = await response.json();
        setValidEndSquares(data.validEndSquares);
        setPromotion(data.promotion || false);
    }

    const letAIMove = async () => {
        const response = await fetch("${API_URL}/let-ai-move");
        const data = await response.json();
        setAiScore(data.score);
        setTurnWhite(prev => !prev);
        setBoard(data.board_history[data.board_history.length - 1]);
        setBoardHistory(data.board_history);
        setMovesHistory(data.moves_history);

        const soundToPlay = data.is_capture ? '/move_capture.mp3' : '/move_from_ai.mp3';
        playSound(soundToPlay);

        if (data.gameStatus.gameIsFinished) {
            setGameFinished(true);
            setWinner(data.gameStatus.winner);
        }
    }

    const handlePromote = async (pieceType: string) => {
        if (!selectedSquareStart || !pendingEndpos) return;

        const moveResult = await makeMove(selectedSquareStart, pendingEndpos, pieceType);

        setPromotionPanelOpen(false);
        setSelectedSquareStart(null);
        setPendingEndpos(null);

        if (!moveResult.gameStatus.gameIsFinished) {
            await letAIMove();
        }
    }

    const handleCancelPromotion = async () => {
        setPromotionPanelOpen(false);
        setSelectedSquareStart(null);
        setPendingEndpos(null);
    }

    const handleSquareClick = async (row: number, col: number) => {
        if (!board) return;
        if (boardHistory && JSON.stringify(board) !== JSON.stringify(boardHistory[boardHistory.length - 1])) return;
        if (humanIsWhite !== turnWhite) return;

        const piece = board[row][col];
        const isHumanPiece = humanIsWhite ? piece > 0 : piece < 0;

        // Case 1: There is no selection and the player clicks on their piece.
        if (!selectedSquareStart && isHumanPiece) {
            setSelectedSquareStart([row, col]);
            showValidEndSquares([row, col]);
            return;
        }

        // Caso 2: There is selection
        if (selectedSquareStart) {

            

            // If player clicks on the same square, deselect
            if (selectedSquareStart[0] === row && selectedSquareStart[1] === col) {
                setSelectedSquareStart(null);
                setValidEndSquares(null);
                return;
            }

            // If player clicks on another piece of theirs, set the new piece as selected
            if (isHumanPiece) {
                setSelectedSquareStart([row, col]);
                showValidEndSquares([row, col]);
                return;
            }

            // Check if the destination is valid
            const isValidMove = validEndSquares?.some(square => square[0] === row && square[1] === col);
            if (!isValidMove){
                setSelectedSquareStart(null);
                setValidEndSquares(null);
                return;
            }

            // If user clicks on a valid destination, check if promotion is needed
            if (promotion) {
                setPendingEndpos([row, col]);
                setPromotionPanelOpen(true);
                setValidEndSquares(null);
            } else {
                setSelectedSquareStart(null);
                setValidEndSquares(null);

                const moveResult = await makeMove(selectedSquareStart, [row, col]);

                if (!moveResult.gameStatus.gameIsFinished) {
                    await letAIMove();
                }                
            }

        }
    }

        

    return(
        <div>
            <div className="flex flex-col items-center">
                
                <div>
                    {board ? (<Squares activepiece={selectedSquareStart} validEndSquares={validEndSquares} board={board} onSquareClick={handleSquareClick} humanIsWhite={humanIsWhite}/>): (<p>Loading board...</p>) }
                </div>
            </div>

            <div className="flex items-center justify-center">
                {gamefinished  && <NewGamePanel winner= {winner} onStartGame={(color) => startNewGame(color)}/>}
            </div>

        <PromotionPanel isOpen={promotionPanelOpen} onCancel={handleCancelPromotion} onPromote={handlePromote} turnWhite={turnWhite}/>
        
        </div>
    )
}