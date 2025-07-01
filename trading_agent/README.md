# Crypto Trading Agent Prototype

This project is a prototype for a cryptocurrency trading agent. It is designed to monitor specified cryptocurrencies (BTC, ETH, BNB, SOL), analyze market data for support and resistance levels, and make simulated trading decisions.

## Key Features (Prototype Stage)

*   **Symbol Monitoring**: Monitors BTC, ETH, BNB, and SOL (configurable).
*   **Data Handling**: Includes a placeholder for fetching market data (simulated with random data). In a real application, this would connect to a cryptocurrency exchange API.
*   **Strategy Engine**:
    *   Identifies basic support and resistance levels.
    *   Placeholder for chart pattern analysis.
    *   Generates BUY/HOLD signals based on proximity to S/R levels.
    *   Includes conceptual elements inspired by Mark Douglas's "Trading in the Zone" regarding risk management, probabilities, and disciplined execution.
*   **Trading Agent**:
    *   Orchestrates data fetching, strategy application, and simulated trade execution.
    *   Manages a simulated portfolio (cash and asset holdings).
    *   Checks for simulated stop-loss and take-profit triggers.
*   **Simulated Trading**: All trading activity is simulated. **No real funds are used, and no actual trades are placed on any exchange.**

## Structure

*   `main.py`: Main entry point to run the trading agent.
*   `core/`: Contains the core logic for the agent and trading strategy.
    *   `agent.py`: The `TradingAgent` class that manages the overall trading process.
    *   `strategy.py`: The `TradingStrategy` class that defines how trading decisions are made.
*   `data/`: Contains data handling modules.
    *   `data_handler.py`: Responsible for fetching and preprocessing market data (currently simulated).
*   `utils/`: (Currently empty) Intended for utility functions.
*   `requirements.txt`: Lists project dependencies (currently minimal for the prototype).

## "Trading in the Zone" Integration

This prototype attempts to incorporate some high-level concepts from "Trading in the Zone" by Mark Douglas:

*   **Risk Management**: The strategy defines risk per trade, and the agent calculates position sizes accordingly. Stop-losses are used.
*   **Probabilistic Mindset**: Comments throughout the code emphasize that trading edges are about higher probabilities, not certainties.
*   **Discipline & Objectivity**: The agent is designed to follow its rules systematically.
*   **Accepting Risk**: The agent executes trades when its predefined criteria (edge) are met.

This integration is conceptual and reflected in the agent's design philosophy and comments, rather than through advanced machine learning from the book's text.

## How to Run (Conceptual)

1.  Ensure you have Python installed.
2.  If there were dependencies, you would install them: `pip install -r requirements.txt`
3.  Navigate to the `trading_agent` directory.
4.  Run the main application: `python main.py`

The agent will start, simulate fetching data, and print its actions to the console.

## Disclaimer

**This is a prototype for educational and illustrative purposes only.**
The market data is simulated, trading logic is simplified, and it does not connect to any live trading environment.
**DO NOT use this code for actual trading or financial decisions.** Financial markets involve significant risk of loss.

---

*Prototype developed by AI.*
