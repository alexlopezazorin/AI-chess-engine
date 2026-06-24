'use client'

import { useChessGame } from '@/contexts/ChessGameContext';
import { useRef, useEffect } from 'react';

export default function LateralPanel() {
    const { movesHistory, setBoard, board, boardHistory, setSelectedSquareStart, setValidEndSquares } = useChessGame();
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    const whiteMoves = movesHistory.filter((_, i) => i % 2 === 0);
    const blackMoves = movesHistory.filter((_, i) => i % 2 === 1);
    const numMoves = Math.ceil(movesHistory.length / 2);

    useEffect(() => {
        if (scrollContainerRef.current) {
            scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
        }
    }, [numMoves]);

    const handleFirstMove = () => {
        setSelectedSquareStart(null);
        setValidEndSquares(null);
        if (boardHistory && boardHistory.length > 0) {
            setBoard(boardHistory[0]);
        }
    };

    const handlePreviousMove = () => {
        setSelectedSquareStart(null);
        setValidEndSquares(null);
        if (boardHistory && board) {
            const currentIndex = boardHistory.findIndex(b => JSON.stringify(b) === JSON.stringify(board));
            if (currentIndex > 0) {
                setBoard(boardHistory[currentIndex - 1]);
            }
        }
    };

    const handleNextMove = () => {
        setSelectedSquareStart(null);
        setValidEndSquares(null);
        if (boardHistory && board) {
            const currentIndex = boardHistory.findIndex(b => JSON.stringify(b) === JSON.stringify(board));
            if (currentIndex < boardHistory.length - 1) {
                setBoard(boardHistory[currentIndex + 1]);
            }
        }
    };

    const handleLastMove = () => {
        setSelectedSquareStart(null);
        setValidEndSquares(null);
        if (boardHistory && boardHistory.length > 0) {
            setBoard(boardHistory[boardHistory.length - 1]);
        }
    };

    return (
        <div className="ml-2 w-80 h-128 bg-gray-200 pt-2 text-center flex flex-col">
            <div>
                <p className="text-xl">Move History</p>
                <div className="mt-1 h-0.5 bg-gray-700"></div>
            </div>

            <div ref={scrollContainerRef} className="mt-4 mb-2 px-4 w-full h-full overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700">
                <div className="flex px-4">
                    <div className="w-auto gap-1 flex flex-col">
                        {Array.from({ length: numMoves }).map((_, i) => (
                            <p key={i}>{i + 1}.</p>
                        ))}
                    </div>

                    <div className="ml-16 gap-8 flex flex-row">
                        <div className="flex-1 gap-1 flex flex-col">
                            {whiteMoves.map((move, i) => (
                                <p key={i} className="bg-white rounded-2xl px-2">{move}</p>
                            ))}
                        </div>

                        <div className="flex-1">
                            <div className="flex-1 gap-1 flex flex-col">
                                {blackMoves.map((move, i) => (
                                    <p key={i} className="bg-white rounded-2xl px-2">{move}</p>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="mb-2 h-0.5 bg-gray-700"></div>

            <div className="mt-auto mb-2 px-2 flex flex-row justify-center gap-2">
                <button onClick={handleFirstMove} className="w-12 h-12 bg-gray-700 text-white rounded-2xl flex items-center justify-center hover:cursor-pointer hover:scale-105 active:scale-95">{"<<"}</button>
                <button onClick={handlePreviousMove} className="w-12 h-12 bg-gray-700 text-white rounded-2xl flex items-center justify-center hover:cursor-pointer hover:scale-105 active:scale-95">{"<"}</button>
                <button onClick={handleNextMove} className="w-12 h-12 bg-gray-700 text-white rounded-2xl flex items-center justify-center hover:cursor-pointer hover:scale-105 active:scale-95">{">"}</button>
                <button onClick={handleLastMove} className="w-12 h-12 bg-gray-700 text-white rounded-2xl flex items-center justify-center hover:cursor-pointer hover:scale-105 active:scale-95">{">>"}</button>
            </div>
        </div>
    );
}