'use client';

import ChessPieces from "../squares/pieces";
import { useState } from 'react';

export default function WelcomePanel({winner, onStartGame}: {winner: string | null, onStartGame: (color: 'white' | 'black' | 'random') => void }) {
    const [color, setColor] = useState<'white' | 'black' | 'random'>('white');


    function onChangeGameColor(gamecolor: string) {
        if (gamecolor === 'white') {
            setColor('white');
        } else if (gamecolor === 'random') {
            setColor('random');
        } else {
            setColor('black');
        }
    }
    return (
        <div className="fixed inset-0 bg-transparent flex items-center justify-center text-center">
            <div className="bg-white p-8 rounded-lg shadow-2xl relative">
                
                {winner ? (
                    winner === 'white' ? <p className="text-lg font-bold">White wins</p>
                    : winner === 'black' ? <p className="text-lg font-bold">Black wins</p>
                    : <p className="text-lg font-bold">Draw!</p>
                ) : <p className="text-lg font-bold">Welcome to the Chess Engine!</p>}

                <div className="mt-4">
                    <p>New Game</p>
                </div>

                <div className="flex flex-row justify-center gap-2 mt-4">
                    <button onClick={() => onChangeGameColor('white')} className={`bg-gray-300 w-16 h-16 flex items-center justify-center rounded-2xl ${color === 'white' ? 'ring-4 ring-blue-500' : ''} hover:bg-gray-200 cursor-pointer`}><ChessPieces piece={100} /></button>
                    <button onClick={() => onChangeGameColor('random')} className={`bg-gray-300 w-16 h-16 flex items-center justify-center rounded-2xl ${color === 'random' ? 'ring-4 ring-blue-500' : ''} hover:bg-gray-200 cursor-pointer`}><img src="/question-mark.svg" alt="?" style={{ width: 45, height: 45 }}/></button>
                    <button onClick={() => onChangeGameColor('black')} className={`bg-gray-300 w-16 h-16 flex items-center justify-center rounded-2xl ${color === 'black' ? 'ring-4 ring-blue-500' : ''} hover:bg-gray-200 cursor-pointer`}><ChessPieces piece={-100} /></button>
                </div>

                <div className="flex justify-center mt-4">
                    <button onClick={() => onStartGame(color)} className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-500 cursor-pointer">
                        Start Game
                    </button>
                </div>
            </div>
        </div>
    );
}