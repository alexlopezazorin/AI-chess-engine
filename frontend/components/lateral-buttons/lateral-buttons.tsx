'use client'

import {RefreshCw, SquarePlus} from 'lucide-react';
import { useChessGame } from '@/contexts/ChessGameContext';

export default function LateralButtons() {
    const { setGameFinished, setWinner, boardflipped, setBoardFlipped, setSelectedSquareStart, setValidEndSquares } = useChessGame();

    const handleNewGame = () => {
        setSelectedSquareStart(null);
        setValidEndSquares(null);
        setGameFinished(true);
        setWinner(null);
    };

    const handleTurnBoard = () => {
        setSelectedSquareStart(null);
        setValidEndSquares(null);
        setBoardFlipped(!boardflipped);
    };

    return (
        <div className="mr-2 flex flex-col h-128">
            <div className="mt-auto flex flex-col gap-2">
                <div className="group relative flex flex-row justify-end items-center">
                    <div className="invisible group-hover:visible mr-2 bg-gray-700 text-white px-2 py-1 h-8 rounded text-sm"> New Game </div>
                    <button onClick={handleNewGame} className="w-14 h-14 bg-slate-400 text-xl text-white rounded-2xl flex items-center justify-center hover:cursor-pointer hover:scale-105 active:scale-95"><SquarePlus /></button>
                </div>
                <div className="group relative flex flex-row  justify-end items-center">
                    <div className="invisible group-hover:visible mr-2 bg-gray-700 text-white px-2 py-1 h-8 rounded text-sm"> Turn board </div>
                    <button onClick={handleTurnBoard} className="w-14 h-14 bg-gray-500 text-xl text-white rounded-2xl flex items-center justify-center hover:cursor-pointer hover:scale-105 active:scale-95"><RefreshCw /></button>
                </div>
            </div>
        </div>
    )
}