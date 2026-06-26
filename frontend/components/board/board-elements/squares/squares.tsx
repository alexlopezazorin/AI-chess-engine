import Pieces from "./pieces";
import {useState} from "react";
import {useChessGame} from "@/contexts/ChessGameContext";

export default function Squares({activepiece, validEndSquares, board, onSquareClick, humanIsWhite}: {activepiece: number[] | null, validEndSquares: number[][] | null, board: number[][], onSquareClick: (row: number, col: number) => void, humanIsWhite: boolean | null}) {

    const { boardflipped } = useChessGame();

    const ispieceActive = (row: number, col: number): boolean => {
        return activepiece !== null && activepiece[0] === row && activepiece[1] === col;
    };

    const isValidEndSquare = (row: number, col: number): boolean => {
        
        if (validEndSquares !== null)
            for (let i = 0; i < validEndSquares.length; i++) {
                if (validEndSquares[i][0] === row && validEndSquares[i][1] === col) {
                    return true;
                }
            }
        return false;
    };

    const getSquareColor = (row: number, col: number): string => {
        const isLight = (row + col) % 2 === 0;
        return isLight ? 'bg-gray-200' : 'bg-gray-700';
    };
    
    const getDisplayCoordinates = (displayRow: number, displayCol: number): [number, number] => {
        const showNormal = (humanIsWhite && !boardflipped) || (!humanIsWhite && boardflipped);
        const actualRow = showNormal ? displayRow : 7 - displayRow;
        const actualCol = showNormal ? displayCol : 7 - displayCol;
        return [actualRow, actualCol];
    };

    return (
        <div className="inline-grid gap-0" style={{ gridTemplateColumns: 'repeat(8, 1fr)' }}>
            {Array(8).fill(null).map((_, displayRow) =>
                Array(8).fill(null).map((_, displayCol) => {
                    const [row, col] = getDisplayCoordinates(displayRow, displayCol);

                    return (
                        <button
                        key={`${displayRow}-${displayCol}`}
                        className={`relative w-10 h-10 md:w-16 md:h-16 flex items-center justify-center ${getSquareColor(row, col)} ${ispieceActive(row, col) ? 'focus:ring-3 focus:ring-blue-500 focus:z-10' : ''}`}
                        onClick={() => onSquareClick(row, col)}
                        >
                            <div>
                                <Pieces piece={board[row][col]}/>
                            </div>

                            {activepiece !== null && isValidEndSquare(row, col) ?
                                ((board[row][col] === 0) ? <div className="absolute w-2 h-2 md:w-3 md:h-3 bg-green-700 rounded-full"></div> : <div className="absolute w-12 h-12 border-4 border-green-700 rounded-full"></div>)
                                : ''}
                        </button>

                    );
                })
            )}
        </div>
    );
}