'use client'

import { createContext, useContext, useState, ReactNode } from 'react';

interface ChessGameContextType {
  gamefinished: boolean;
  setGameFinished: (value: boolean) => void;
  winner: string | null;
  setWinner: (value: string | null) => void;
  boardflipped: boolean;
  setBoardFlipped: (value: boolean) => void;
  movesHistory: string[];
  setMovesHistory: (value: string[]) => void;
  board: number[][] | null;
  setBoard: (value: number[][] | null) => void;
  boardHistory: number[][][] | null;
  setBoardHistory: (value: number[][][] | null) => void;
  aiScore: number;
  setAiScore: (value: number) => void;
  selectedSquareStart: number[] | null;
  setSelectedSquareStart: (value: number[] | null) => void;
  validEndSquares: number[][] | null;
  setValidEndSquares: (value: number[][] | null) => void;
}

const ChessGameContext = createContext<ChessGameContextType | undefined>(undefined);

export function ChessGameProvider({ children }: { children: ReactNode }) {
  const [gamefinished, setGameFinished] = useState(true);
  const [winner, setWinner] = useState<string | null>(null);
  const [boardflipped, setBoardFlipped] = useState(false);
  const [movesHistory, setMovesHistory] = useState<string[]>([]);
  const [board, setBoard] = useState<number[][] | null>(null);
  const [boardHistory, setBoardHistory] = useState<number[][][] | null>(null);
  const [aiScore, setAiScore] = useState(0.00);
  const [selectedSquareStart, setSelectedSquareStart] = useState<number[] | null>(null);
  const [validEndSquares, setValidEndSquares] = useState<number[][] | null>(null);

  return (
    <ChessGameContext.Provider
      value={{
        gamefinished,
        setGameFinished,
        winner,
        setWinner,
        boardflipped,
        setBoardFlipped,
        movesHistory,
        setMovesHistory,
        board,
        setBoard,
        boardHistory,
        setBoardHistory,
        aiScore,
        setAiScore,
        selectedSquareStart,
        setSelectedSquareStart,
        validEndSquares,
        setValidEndSquares,
      }}
    >
      {children}
    </ChessGameContext.Provider>
  );
}

export function useChessGame() {
  const context = useContext(ChessGameContext);
  return context;
}
