import ChessPieces from '../squares/pieces';

export default function PromotionPanel({ isOpen, onCancel, onPromote, turnWhite }: { isOpen: boolean, onCancel: () => void, onPromote: (piece: string) => void, turnWhite: boolean }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-transparent flex items-center justify-center">
      <div className="bg-white p-4 rounded-lg shadow-lg">
        <div className="flex justify-end mb-4">
          <button
            onClick={onCancel}
            className="text-2xl font-bold cursor-pointer right-0 top-0 text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        <div className="flex gap-4 justify-center">
          <button onClick={() => onPromote('queen')} className="w-16 h-16 flex items-center justify-center cursor-pointer bg-gray-200 rounded">
            <ChessPieces piece={turnWhite? 9 : -9} />
          </button>
          <button onClick={() => onPromote('rook')} className="w-16 h-16 flex items-center justify-center cursor-pointer bg-gray-200 rounded">
            <ChessPieces piece={turnWhite? 5 : -5} />
          </button>
          <button onClick={() => onPromote('bishop')} className="w-16 h-16 flex items-center justify-center cursor-pointer bg-gray-200 rounded">
            <ChessPieces piece={turnWhite? 3 : -3} />
          </button>
          <button onClick={() => onPromote('knight')} className="w-16 h-16 flex items-center justify-center cursor-pointer bg-gray-200 rounded">
            <ChessPieces piece={turnWhite? 2 : -2} />
          </button>
        </div>
      </div>
    </div>
  );
}
