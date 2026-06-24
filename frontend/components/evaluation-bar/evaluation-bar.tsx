'use client'

import { useChessGame } from '@/contexts/ChessGameContext';

export default function EvaluationBar() {
    const { aiScore } = useChessGame();

    const calculateBarWidth = () => {
        const percentage = Math.max(1, Math.min(99, 50 + (aiScore / 5 * 49)));
        return `${percentage}%`;
    };

    return (
        <div className="flex flex-col">
            <div className="text-center text-xl">Evaluation: {aiScore}</div>

            <div className="mt-1 w-160 h-8 bg-gray-700 rounded-2xl overflow-hidden border-2 border-gray-900">
                <div style={{ width: calculateBarWidth() }} className="h-full bg-white rounded-2xl transition-all duration-300"></div>
            </div>
        </div>
    );
}