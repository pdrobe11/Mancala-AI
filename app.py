import streamlit as st
from PIL import Image
from mancala_engine import build_board, top_moves, game_over, sweep

st.set_page_config(page_title="Mancala AI", page_icon="🟤", layout="centered")

st.title("🟤 Mancala AI")
st.caption("Upload a GamePigeon screenshot, verify the stone counts, and get the top three moves.")

st.info(
    "This first version uses screenshot upload plus manual board verification. "
    "It does not yet count stones automatically. A sample GamePigeon screenshot "
    "is needed to calibrate reliable visual recognition."
)

uploaded = st.file_uploader("Upload a screenshot of your current game", type=["png", "jpg", "jpeg"])
if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Your GamePigeon board", use_container_width=True)

st.subheader("Enter the board")
st.caption("Enter pits from left to right as you see them on your side. "
           "For the opponent, enter their pits from their left to right.")

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Your six pits**")
    your_pits = [
        st.number_input(f"Your pit {i+1}", min_value=0, max_value=48, value=4, step=1, key=f"you{i}")
        for i in range(6)
    ]
    your_store = st.number_input("Your store", min_value=0, max_value=48, value=0, step=1)
with c2:
    st.markdown("**Opponent's six pits**")
    opponent_pits = [
        st.number_input(f"Opponent pit {i+1}", min_value=0, max_value=48, value=4, step=1, key=f"opp{i}")
        for i in range(6)
    ]
    opponent_store = st.number_input("Opponent's store", min_value=0, max_value=48, value=0, step=1)

side = st.radio("Whose turn is it?", ["Your turn", "Opponent's turn"], horizontal=True)
depth = st.select_slider("Search depth", options=[6, 8, 10, 12, 14], value=10,
                         help="Higher depth examines more future turns and may take longer.")
if st.button("Analyze best moves", type="primary", use_container_width=True):
    try:
        board = build_board(
            [int(x) for x in your_pits],
            [int(x) for x in opponent_pits],
            int(your_store), int(opponent_store), 0
        )
        player = 0 if side == "Your turn" else 1
        if game_over(board):
            st.success("The game is already over.")
            final = sweep(board)
            st.write(f"Your final store: {final[6]} · Opponent final store: {final[13]}")
        else:
            with st.spinner("Searching possible moves..."):
                results = top_moves(board, player, depth=int(depth))
            if not results:
                st.warning("No legal moves found. Check the board counts.")
            else:
                st.subheader("Your top three moves" if player == 0 else "Opponent's top three moves")
                for rank, move in enumerate(results, 1):
                    st.markdown(f"### {rank}. Play pit {move['pit']}")
                    st.write(move["explanation"])
                    st.caption(f"Search score: {move['score']:.2f} · Extra turn: {'Yes' if move['extra_turn'] else 'No'}")
                st.caption("Scores are search evaluations, not probabilities of winning. The engine assumes standard Kalah rules.")
    except Exception as exc:
        st.error(str(exc))

st.divider()
st.caption("Rule assumption: standard 6-pit Kalah, 4 stones initially per pit, store skip, capture rule, extra turns, and final sweep.")
