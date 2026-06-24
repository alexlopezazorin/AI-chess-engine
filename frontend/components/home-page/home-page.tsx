import Board from "../board/board";
import LateralPanel from "../lateral-panel/lateral-panel";
import LateralButtons from "../lateral-buttons/lateral-buttons";
import EvaluationBar from "../evaluation-bar/evaluation-bar";
import { ChessGameProvider } from "@/contexts/ChessGameContext";

export default function HomePage() {
    return(
        <ChessGameProvider>
            <div>
                <div className="text-center mt-2">
                    <h1 className="text-4xl">Chess Engine</h1>
                    <p>created by <span className="inline-block hover:-translate-y-1 transition-transform"><a href="https://www.linkedin.com/in/alejandro-lopez-azorin/">alexlopezazorin@gmail.com </a></span></p>
                </div>

                <div className="mt-4 flex flex-row justify-center">
                    <LateralButtons/>
                    <Board/>
                    <LateralPanel/>
                </div>

                <div className="mt-4 flex justify-center">
                    <EvaluationBar/>
                </div>
            </div>
        </ChessGameProvider>
    );
}