const pieceMap: Record<number, { path: string}> = {
    1: { path: "wp.svg"},
    2: { path: "wn.svg"},
    3: { path: "wb.svg"},
    5: { path: "wr.svg"},
    9: { path: "wq.svg"},
    100: { path: "wk.svg"},
    "-1": { path: "bp.svg"},
    "-2": { path: "bn.svg"},
    "-3": { path: "bb.svg"},
    "-5": { path: "br.svg"},
    "-9": { path: "bq.svg"},
    "-100": { path: "bk.svg"},
};

export default function Pieces({ piece }: { piece: number }) {

    if (piece === 0) return null;
    const pieceData = pieceMap[piece].path;

    if (!pieceData) return null;

    return (
        <img src={`/${pieceData}`} className="w-full h-full hover:scale-105 active:scale-95 cursor-pointer"/>
    );
}