import Board from "../board/board";

export default function HomePage() {
    return(
        <div>
            <div className="text-center mt-2">
                <h1 className="text-4xl">Chess Engine</h1>
                <p>created by <span className="inline-block hover:-translate-y-1 transition-transform"><a href="https://www.linkedin.com/in/alejandro-lopez-azorin/">alexlopezazorin@gmail.com </a></span></p>
            </div>

            <div className="mt-4">
                <Board/>
                {/*<LateralPanel/>*/}
                {/*<LateralButtons/>*/}
            </div>
            
            <div>
                {/*<EvaluationBar/>*/}
            </div>
            
            {/*<NewGamePanel/>*/}

            {/*<GameFinishedPanel/>*/}
        
        </div>
);
}