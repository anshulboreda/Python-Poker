import sys
import random
import collections
import itertools
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_ESCAPE
# Texas Hold'em Poker Game with Pygame

# Pygame initialization
pygame.init()
pygame.font.init()

# Screen setup
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Texas Hold'em Poker")

# Colors
BACKGROUND_COLOR = (0, 100, 0)  # Green felt
PLAYER_BG_COLOR = (25, 25, 112)  # Dark blue
PLAYER_ACTIVE_COLOR = (70, 130, 180)  # Steel blue
BUTTON_COLOR = (210, 180, 140)  # Tan
BUTTON_HOVER_COLOR = (230, 200, 160)  # Light tan
TEXT_COLOR = (255, 255, 255)  # White
CHIP_COLORS = {
    'white': (255, 255, 255),
    'red': (220, 20, 60),
    'blue': (30, 144, 255),
    'green': (50, 205, 50),
    'black': (0, 0, 0)
}

# Fonts
FONT_SMALL = pygame.font.SysFont('Arial', 16)
FONT_MEDIUM = pygame.font.SysFont('Arial', 20)
FONT_LARGE = pygame.font.SysFont('Arial', 24)
FONT_TITLE = pygame.font.SysFont('Arial', 32, bold=True)

# Card dimensions
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_CORNER_RADIUS = 5
CARD_SPACING = 20

# Player positions
PLAYER_POSITIONS = [
    (SCREEN_WIDTH // 2, 650),  # Bottom (human player)
    (SCREEN_WIDTH - 200, 500),  # Right
    (SCREEN_WIDTH - 300, 300),  # Top-right
    (SCREEN_WIDTH // 2, 150),   # Top
    (300, 300),                 # Top-left
    (200, 500)                  # Left
]

# Constants (from the original code)
RANKS_STR = "23456789TJQKA"
SUITS_STR = "CDHS"  # Clubs, Diamonds, Hearts, Spades
RANK_MAP = {rank: i for i, rank in enumerate(RANKS_STR)}
RANK_MAP_REV = {i: rank for rank, i in RANK_MAP.items()}

HIGH_CARD = 0
ONE_PAIR = 1
TWO_PAIR = 2
THREE_OF_A_KIND = 3
STRAIGHT = 4
FLUSH = 5
FULL_HOUSE = 6
FOUR_OF_A_KIND = 7
STRAIGHT_FLUSH = 8
ROYAL_FLUSH = 9

HAND_RANK_NAMES = {
    ROYAL_FLUSH: "Royal Flush",
    STRAIGHT_FLUSH: "Straight Flush",
    FOUR_OF_A_KIND: "Four of a Kind",
    FULL_HOUSE: "Full House",
    FLUSH: "Flush",
    STRAIGHT: "Straight",
    THREE_OF_A_KIND: "Three of a Kind",
    TWO_PAIR: "Two Pair",
    ONE_PAIR: "One Pair",
    HIGH_CARD: "High Card"
}

# Button class for UI
class TextInput:
    def __init__(self, x, y, width, height, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 255, 255)
        self.text = ""
        self.font = pygame.font.SysFont('Arial', font_size)
        self.active = False
        self.blink = True
        self.blink_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isdigit():
                    self.text += event.unicode
        return False

    def update(self):
        self.blink_timer += 1
        if self.blink_timer >= 30:
            self.blink = not self.blink
            self.blink_timer = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, 2)
        pygame.draw.rect(surface, (240, 240, 240), self.rect)
        
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        
        if self.active and self.blink:
            cursor_x = self.rect.x + 5 + text_surface.get_width()
            pygame.draw.line(surface, (0, 0, 0), 
                           (cursor_x, self.rect.y + 5),
                           (cursor_x, self.rect.y + self.rect.height - 5), 2)

    def get_value(self):
        return int(self.text) if self.text else 0
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        
    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=5)
        
        text_surf = FONT_MEDIUM.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                return self.action
        return None

# Card class with graphical representation
class Card:
    def __init__(self, rank_str, suit_str):
        if rank_str not in RANKS_STR:
            raise ValueError(f"Invalid rank: {rank_str}")
        if suit_str not in SUITS_STR:
            raise ValueError(f"Invalid suit: {suit_str}")
        
        self.rank_str = rank_str
        self.suit_str = suit_str
        self.rank = RANK_MAP[rank_str]  # Numerical rank
        self.suit = SUITS_STR.index(suit_str)  # Numerical suit
        self.face_up = True
        
    def __str__(self):
        return f"{self.rank_str}{self.suit_str}"

    def __repr__(self):
        return f"Card('{self.rank_str}', '{self.suit_str}')"

    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit
    
    def __lt__(self, other):  # For sorting
        if self.rank == other.rank:
            return self.suit < other.suit
        return self.rank < other.rank
    
    def __hash__(self):  # To be used in sets
        return hash((self.rank, self.suit))
    
    def draw(self, surface, x, y, width=CARD_WIDTH, height=CARD_HEIGHT):
        if not self.face_up:
            # Draw card back
            pygame.draw.rect(surface, (30, 30, 150), (x, y, width, height), border_radius=CARD_CORNER_RADIUS)
            pygame.draw.rect(surface, (50, 50, 200), (x+5, y+5, width-10, height-10), border_radius=CARD_CORNER_RADIUS)
            pygame.draw.rect(surface, (70, 70, 220), (x+10, y+10, width-20, height-20), border_radius=CARD_CORNER_RADIUS)
            return
            
        # Draw card front
        pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), border_radius=CARD_CORNER_RADIUS)
        pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 2, border_radius=CARD_CORNER_RADIUS)
        
        # Set color based on suit
        suit_colors = {'C': (0, 0, 0), 'D': (200, 0, 0), 'H': (200, 0, 0), 'S': (0, 0, 0)}
        color = suit_colors[self.suit_str]
        
        # Draw rank and suit in top-left
        rank_surf = FONT_MEDIUM.render(self.rank_str, True, color)
        suit_surf = FONT_MEDIUM.render(self.suit_str, True, color)
        surface.blit(rank_surf, (x + 5, y + 5))
        surface.blit(suit_surf, (x + 5, y + 25))
        
        # Draw large suit symbol in center
        suit_symbols = {'C': '♣', 'D': '♦', 'H': '♥', 'S': '♠'}
        symbol = suit_symbols[self.suit_str]
        symbol_surf = FONT_LARGE.render(symbol, True, color)
        symbol_rect = symbol_surf.get_rect(center=(x + width//2, y + height//2))
        surface.blit(symbol_surf, symbol_rect)
        
        # Draw rank and suit in bottom-right (rotated)
        rank_surf_rot = pygame.transform.rotate(rank_surf, 180)
        suit_surf_rot = pygame.transform.rotate(suit_surf, 180)
        surface.blit(rank_surf_rot, (x + width - 25, y + height - 25))
        surface.blit(suit_surf_rot, (x + width - 25, y + height - 45))

# Deck class remains the same
class Deck:
    def __init__(self):
        self.cards = [Card(r, s) for r in RANKS_STR for s in SUITS_STR]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_cards=1):
        if num_cards == 1:
            return self.cards.pop() if self.cards else None
        dealt = []
        for _ in range(num_cards):
            if self.cards:
                dealt.append(self.cards.pop())
            else:
                break  # Should not happen in a normal game
        return dealt
    
    def __len__(self):
        return len(self.cards)

# HandEvaluator class remains the same
class HandEvaluator:
    def get_best_hand(self, seven_cards):
        if len(seven_cards) < 5:
            return (HIGH_CARD, [c.rank for c in sorted(seven_cards, reverse=True)], seven_cards)

        best_rank_tuple = (HIGH_CARD, [-1], [])  # (rank_code, tie_breakers, cards)

        for five_card_combo in itertools.combinations(seven_cards, 5):
            current_rank_tuple = self._evaluate_5_card_hand(list(five_card_combo))
            if self._compare_rank_tuples(current_rank_tuple, best_rank_tuple) > 0:
                best_rank_tuple = current_rank_tuple
        
        return best_rank_tuple[0], best_rank_tuple[1], list(best_rank_tuple[2])

    def _compare_rank_tuples(self, rank_tuple1, rank_tuple2):
        if rank_tuple1[0] != rank_tuple2[0]:
            return rank_tuple1[0] - rank_tuple2[0]
        
        for tb1, tb2 in zip(rank_tuple1[1], rank_tuple2[1]):
            if tb1 != tb2:
                return tb1 - tb2
        return 0

    def _evaluate_5_card_hand(self, hand_cards):  # Expects exactly 5 cards
        hand_cards.sort(key=lambda c: c.rank, reverse=True)
        ranks = [card.rank for card in hand_cards]
        suits = [card.suit for card in hand_cards]
        
        rank_counts = collections.Counter(ranks)
        sorted_rank_counts = sorted(rank_counts.items(), key=lambda item: (item[1], item[0]), reverse=True)

        is_flush = len(set(suits)) == 1
        
        is_straight = False
        unique_sorted_ranks = sorted(list(set(ranks)), reverse=True)
        if len(unique_sorted_ranks) >= 5:
            if all(r in unique_sorted_ranks for r in [RANK_MAP['A'], RANK_MAP['2'], RANK_MAP['3'], RANK_MAP['4'], RANK_MAP['5']]):
                is_straight = True
                straight_high_rank = RANK_MAP['5']
            else:
                for i in range(len(unique_sorted_ranks) - 4):
                    if unique_sorted_ranks[i] - unique_sorted_ranks[i+4] == 4:
                        is_straight = True
                        straight_high_rank = unique_sorted_ranks[i]
                        break
        
        if is_straight and is_flush:
            if straight_high_rank == RANK_MAP['A']:
                return (ROYAL_FLUSH, [straight_high_rank], hand_cards)
            return (STRAIGHT_FLUSH, [straight_high_rank], hand_cards)

        if sorted_rank_counts[0][1] == 4:
            quad_rank = sorted_rank_counts[0][0]
            kicker = [r for r in ranks if r != quad_rank][0]
            return (FOUR_OF_A_KIND, [quad_rank, kicker], hand_cards)

        if sorted_rank_counts[0][1] == 3 and sorted_rank_counts[1][1] == 2:
            trips_rank = sorted_rank_counts[0][0]
            pair_rank = sorted_rank_counts[1][0]
            return (FULL_HOUSE, [trips_rank, pair_rank], hand_cards)

        if is_flush:
            return (FLUSH, ranks, hand_cards)

        if is_straight:
            return (STRAIGHT, [straight_high_rank], hand_cards)

        if sorted_rank_counts[0][1] == 3:
            trips_rank = sorted_rank_counts[0][0]
            kickers = sorted([r for r in ranks if r != trips_rank], reverse=True)[:2]
            return (THREE_OF_A_KIND, [trips_rank] + kickers, hand_cards)

        if sorted_rank_counts[0][1] == 2 and sorted_rank_counts[1][1] == 2:
            high_pair_rank = sorted_rank_counts[0][0]
            low_pair_rank = sorted_rank_counts[1][0]
            kicker_ranks = [r for r in ranks if r != high_pair_rank and r != low_pair_rank]
            kicker = kicker_ranks[0] if kicker_ranks else -1
            return (TWO_PAIR, [high_pair_rank, low_pair_rank, kicker], hand_cards)

        if sorted_rank_counts[0][1] == 2:
            pair_rank = sorted_rank_counts[0][0]
            kickers = sorted([r for r in ranks if r != pair_rank], reverse=True)[:3]
            return (ONE_PAIR, [pair_rank] + kickers, hand_cards)
        
        return (HIGH_CARD, ranks, hand_cards)

# Player class with graphical representation
class Player:
    def __init__(self, name, chips, is_human=False):
        self.name = name
        self.chips = chips
        self.hole_cards = []
        self.current_bet_in_street = 0
        self.is_folded = False
        self.is_all_in = False
        self.is_human = is_human
        self.last_action = None
        self.position = None
        
    def reset_for_hand(self):
        self.hole_cards = []
        self.current_bet_in_street = 0
        self.is_folded = False
        self.is_all_in = False
        self.last_action = None

    def __str__(self):
        return f"{self.name} ({self.chips} chips)"
    
    def draw(self, surface, x, y, is_active=False):
        # Draw player box
        color = PLAYER_ACTIVE_COLOR if is_active else PLAYER_BG_COLOR
        pygame.draw.rect(surface, color, (x, y, 200, 100), border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), (x, y, 200, 100), 2, border_radius=10)
        
        # Draw player name
        name_surf = FONT_MEDIUM.render(self.name, True, TEXT_COLOR)
        surface.blit(name_surf, (x + 10, y + 10))
        
        # Draw chips
        chips_surf = FONT_MEDIUM.render(f"Chips: {self.chips}", True, TEXT_COLOR)
        surface.blit(chips_surf, (x + 10, y + 35))
        
        # Draw current bet
        bet_surf = FONT_MEDIUM.render(f"Bet: {self.current_bet_in_street}", True, TEXT_COLOR)
        surface.blit(bet_surf, (x + 10, y + 60))
        
        # Draw status
        status = ""
        if self.is_folded:
            status = "FOLDED"
        elif self.is_all_in:
            status = "ALL-IN"
            
        if status:
            status_surf = FONT_MEDIUM.render(status, True, (255, 50, 50))
            surface.blit(status_surf, (x + 120, y + 60))
        
        # Draw cards
        card_x = x + 10
        for card in self.hole_cards:
            # For opponents, only show face up if human or at showdown
            if not self.is_human and not self.is_all_in and not self.is_folded:
                card.face_up = False
            card.draw(surface, card_x, y + 80, CARD_WIDTH//2, CARD_HEIGHT//2)
            card_x += CARD_WIDTH//2 + 5

# EquityCalculator class remains the same
class EquityCalculator:
    def __init__(self, evaluator):
        self.evaluator = evaluator

    def calculate_equity(self, player_hole_cards, board_cards, num_opponents, num_simulations=1000):
        player_wins = 0
        ties = 0

        known_cards = set(player_hole_cards + board_cards)

        for _ in range(num_simulations):
            sim_deck_cards = [Card(r, s) for r in RANKS_STR for s in SUITS_STR]
            current_sim_deck = [card for card in sim_deck_cards if card not in known_cards]
            random.shuffle(current_sim_deck)

            opponent_hands = []
            possible_to_deal = True
            for _ in range(num_opponents):
                if len(current_sim_deck) < 2:
                    possible_to_deal = False
                    break
                opponent_hands.append(current_sim_deck[0:2])
                current_sim_deck = current_sim_deck[2:]
            if not possible_to_deal: continue

            remaining_board_needed = 5 - len(board_cards)
            if len(current_sim_deck) < remaining_board_needed:
                continue
            
            sim_additional_board = current_sim_deck[:remaining_board_needed]
            sim_full_board = board_cards + sim_additional_board

            player_full_hand = player_hole_cards + sim_full_board
            player_rank_tuple = self.evaluator.get_best_hand(player_full_hand)

            best_opponent_rank_tuple = (HIGH_CARD, [-1], [])
            for opp_hole in opponent_hands:
                opp_full_hand = opp_hole + sim_full_board
                opp_rank_tuple = self.evaluator.get_best_hand(opp_full_hand)
                if self.evaluator._compare_rank_tuples(opp_rank_tuple, best_opponent_rank_tuple) > 0:
                    best_opponent_rank_tuple = opp_rank_tuple
            
            comparison = self.evaluator._compare_rank_tuples(player_rank_tuple, best_opponent_rank_tuple)
            if comparison > 0:
                player_wins += 1
            elif comparison == 0:
                ties += 1
        
        return (player_wins + ties / 2) / num_simulations if num_simulations > 0 else 0.0

# Game class with graphical interface
class TexasHoldemGame:
    def __init__(self, player_names_chips, small_blind=50, big_blind=75):
        self.evaluator = HandEvaluator()
        self.equity_calculator = EquityCalculator(self.evaluator)
        self.players = [Player(name, chips, is_human=(i==0)) for i, (name, chips) in enumerate(player_names_chips)]
        self.small_blind_amount = small_blind
        self.big_blind_amount = big_blind
        self.deck = Deck()
        self.board = []
        self.pot = 0
        self.current_street_highest_bet = 0
        self.dealer_pos = -1
        self.current_player_idx = 0
        self.aggressor = None
        self.buttons = []
        self.message = ""
        self.equity_display = ""
        self.game_state = "pre_flop"  # Tracks current game phase
        self.showdown_info = []
        
        # Assign positions to players
        for i, player in enumerate(self.players):
            player.position = PLAYER_POSITIONS[i % len(PLAYER_POSITIONS)]
        
    def _rotate_dealer(self):
        self.dealer_pos = (self.dealer_pos + 1) % len(self.players)

    def _post_blinds(self):
        num_active_players = len([p for p in self.players if p.chips > 0])
        if num_active_players < 2: return False

        sb_player_idx = (self.dealer_pos + 1) % len(self.players)
        bb_player_idx = (self.dealer_pos + 2) % len(self.players)

        if num_active_players == 2:
            sb_player_idx = self.dealer_pos
            bb_player_idx = (self.dealer_pos + 1) % len(self.players)

        sb_player = self.players[sb_player_idx]
        bb_player = self.players[bb_player_idx]

        sb_amount = min(self.small_blind_amount, sb_player.chips)
        sb_player.chips -= sb_amount
        sb_player.current_bet_in_street = sb_amount
        self.pot += sb_amount

        bb_amount = min(self.big_blind_amount, bb_player.chips)
        bb_player.chips -= bb_amount
        bb_player.current_bet_in_street = bb_amount
        self.pot += bb_amount
        
        self.current_street_highest_bet = bb_amount
        self.current_player_idx = (bb_player_idx + 1) % len(self.players)
        self.aggressor = bb_player
        return True

    def _deal_hole_cards(self):
        start_deal_idx = (self.dealer_pos + 1) % len(self.players)
        for i in range(len(self.players) * 2):
            player_to_deal_idx = (start_deal_idx + i) % len(self.players)
            if len(self.players[player_to_deal_idx].hole_cards) < 2:
                self.players[player_to_deal_idx].hole_cards.append(self.deck.deal())
        
    def _get_player_action(self, player):
        min_bet_to_stay = self.current_street_highest_bet - player.current_bet_in_street
        can_check = (min_bet_to_stay == 0)
        
        # Create buttons with proper spacing
        self.buttons = []
        button_y = SCREEN_HEIGHT - 80
        button_width = 100
        button_height = 40
        button_spacing = 10
        
        # Calculate total width of all buttons
        total_buttons_width = (4 * button_width) + (3 * button_spacing)
        start_x = (SCREEN_WIDTH - total_buttons_width) // 2
        
        # Create buttons with proper positioning
        self.buttons.append(Button(  # Fold button
            start_x,
            button_y, 
            button_width, 
            button_height, 
            "Fold", 
            "fold"
        ))
        
        # Check/Call button
        if can_check:
            self.buttons.append(Button(
                start_x + button_width + button_spacing,
                button_y, 
                button_width, 
                button_height, 
                "Check", 
                "check"
            ))
        else:
            call_text = f"Call {min_bet_to_stay}"
            self.buttons.append(Button(
                start_x + button_width + button_spacing,
                button_y, 
                button_width, 
                button_height, 
                call_text, 
                "call"
            ))
        
        # Bet/Raise button
        self.buttons.append(Button(
            start_x + 2*(button_width + button_spacing),
            button_y, 
            button_width, 
            button_height, 
            "Bet/Raise", 
            "raise"
        ))
        
        # All-in button
        self.buttons.append(Button(
            start_x + 3*(button_width + button_spacing),
            button_y, 
            button_width, 
            button_height, 
            "All-in", 
            "allin"
        ))
        
        # Equity button (only after flop)
        if self.board and len(self.board) >= 3:
            self.buttons.append(Button(
                SCREEN_WIDTH - 120,
                button_y - 50,
                100,
                30,
                "Equity",
                "equity"
            ))
        
        # Create text input for bet amount
        bet_input = TextInput(
            start_x + 4*(button_width + button_spacing),
            button_y, 
            100, 
            button_height
        )
        input_active = False
        
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Handle button hover
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    button.check_hover(mouse_pos)
                    action = button.handle_event(event)
                    if action:
                        if action == "raise":
                            input_active = True
                        elif action == "equity":
                            num_opp = len([p for p in self.players if not p.is_folded and p != player])
                            if num_opp > 0:
                                equity_val = self.equity_calculator.calculate_equity(player.hole_cards, self.board, num_opp)
                                self.equity_display = f"Equity: {equity_val*100:.2f}%"
                            else:
                                self.equity_display = "No active opponents"
                        elif action == "call":
                            return action, min_bet_to_stay
                        elif action == "allin":
                            return action, player.chips
                        else:
                            return action, 0  # For fold/check
                
                # Handle bet amount input
                if input_active:
                    if bet_input.handle_event(event):
                        bet_amount = bet_input.get_value()
                        if bet_amount > 0:
                            # Calculate raise amount
                            total_bet = player.current_bet_in_street + bet_amount
                            min_raise = max(
                                self.big_blind_amount,
                                self.current_street_highest_bet + self.big_blind_amount
                            )
                            
                            if total_bet >= min_raise or bet_amount == player.chips:
                                return "raise", bet_amount
                            else:
                                self.message = f"Minimum raise is {min_raise - player.current_bet_in_street}"
                                input_active = False
                        else:
                            input_active = False
            
            # Update bet input cursor blink
            if input_active:
                bet_input.update()
            
            # Draw everything
            self.draw()
            
            # Draw bet input if active
            if input_active:
                bet_input.draw(screen)
                min_raise = max(
                    self.big_blind_amount,
                    self.current_street_highest_bet + self.big_blind_amount - player.current_bet_in_street
                )
                hint_text = FONT_SMALL.render(f"Min: {min_raise}", True, TEXT_COLOR)
                screen.blit(hint_text, (start_x + 4*(button_width + button_spacing), button_y - 20))
            
            pygame.display.flip()
            pygame.time.delay(30)

    def _get_bot_action(self, player):
        # Simplified bot logic (same as before)
        min_bet_to_stay = self.current_street_highest_bet - player.current_bet_in_street
        can_check = (min_bet_to_stay == 0)

        if not self.board:  # Pre-flop
            hole_sum = player.hole_cards[0].rank + player.hole_cards[1].rank
            is_pair = player.hole_cards[0].rank == player.hole_cards[1].rank

            if is_pair and player.hole_cards[0].rank >= RANK_MAP['7']:
                action_type = "raise"
            elif hole_sum >= RANK_MAP['T'] + RANK_MAP['9']:
                action_type = "raise"
            elif hole_sum >= RANK_MAP['8'] + RANK_MAP['7'] or (is_pair and player.hole_cards[0].rank >= RANK_MAP['2']):
                action_type = "call"
            else:
                action_type = "fold"
        else:  # Post-flop
            combined_cards = player.hole_cards + self.board
            rank_code, _, _ = self.evaluator.get_best_hand(combined_cards)

            if rank_code >= ONE_PAIR:
                action_type = "raise" if rank_code >= TWO_PAIR else "call"
            else:
                action_type = "fold"

        # Execute action chosen
        if action_type == "fold":
            if min_bet_to_stay > 0:
                return "fold", 0
            else:
                return "check", 0
        elif action_type == "call":
            if min_bet_to_stay > 0:
                amount_to_call = min(min_bet_to_stay, player.chips)
                return "call", amount_to_call
            else:
                return "check", 0
        elif action_type == "raise":
            raise_amount_val = self.big_blind_amount * 2
            if player.chips > raise_amount_val + min_bet_to_stay:
                actual_bet_amount = min_bet_to_stay + raise_amount_val
                if player.chips >= actual_bet_amount:
                    return "raise", actual_bet_amount
                else:
                    return "allin", player.chips
            elif player.chips > min_bet_to_stay:
                return "call", min(min_bet_to_stay, player.chips)
            elif player.chips > 0:
                return "allin", player.chips
            else:
                return "check", 0

        return "check" if can_check else "fold", 0

    def _betting_round(self, street_name):
        self.message = f"{street_name} Betting Round"
        self.game_state = street_name.lower().replace("-", "_")
        
        num_active_players_in_hand = len([p for p in self.players if not p.is_folded and p.chips > 0])
        if num_active_players_in_hand <= 1:
            return

        if street_name != "Pre-flop":
            for p in self.players:
                if not p.is_all_in:
                    p.current_bet_in_street = 0
            self.current_street_highest_bet = 0
            self.current_player_idx = (self.dealer_pos + 1) % len(self.players)
            self.aggressor = None

        initial_actor_idx = self.current_player_idx
        while self.players[self.current_player_idx].is_folded or self.players[self.current_player_idx].is_all_in:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            if self.current_player_idx == initial_actor_idx:
                return

        actions_this_round = 0
        players_acted_this_betting_level = set()

        round_over = False
        while not round_over:
            num_active_players_in_hand = len([p for p in self.players if not p.is_folded and p.chips > 0])
            if num_active_players_in_hand <= 1:
                break

            player = self.players[self.current_player_idx]

            if player.is_folded or player.is_all_in:
                self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
                continue

            if player.is_human:
                action, amount = self._get_player_action(player)
            else:
                action, amount = self._get_bot_action(player)

            player.last_action = action
            self.message = f"{player.name} {action}s"

            if action == "fold":
                player.is_folded = True
            elif action == "check":
                pass
            elif action == "call":
                actual_call_amount = min(amount, player.chips)
                player.chips -= actual_call_amount
                player.current_bet_in_street += actual_call_amount
                self.pot += actual_call_amount
                if player.chips == 0:
                    player.is_all_in = True
            elif action == "raise":
                actual_raise_amount = min(amount, player.chips)
                player.chips -= actual_raise_amount
                player.current_bet_in_street += actual_raise_amount
                self.pot += actual_raise_amount
                self.current_street_highest_bet = player.current_bet_in_street
                self.aggressor = player
                players_acted_this_betting_level.clear()
                if player.chips == 0:
                    player.is_all_in = True
            elif action == "allin":
                all_in_amount = player.chips
                player.current_bet_in_street += all_in_amount
                self.pot += all_in_amount
                player.chips = 0
                player.is_all_in = True
                if player.current_bet_in_street > self.current_street_highest_bet:
                    self.current_street_highest_bet = player.current_bet_in_street
                    self.aggressor = player
                    players_acted_this_betting_level.clear()

            players_acted_this_betting_level.add(self.current_player_idx)

            all_eligible_acted = True
            all_bets_equalized = True
            
            for i, p_check in enumerate(self.players):
                if p_check.is_folded or p_check.is_all_in:
                    continue
                if i not in players_acted_this_betting_level:
                    all_eligible_acted = False
                    break
                if p_check.current_bet_in_street < self.current_street_highest_bet:
                    all_bets_equalized = False

            is_preflop_bb_option = (street_name == "Pre-flop" and
                                    self.players[self.current_player_idx].current_bet_in_street == self.big_blind_amount and
                                    self.current_street_highest_bet == self.big_blind_amount and
                                    self.aggressor == self.players[(self.dealer_pos + 2)%len(self.players)] and
                                    self.current_player_idx == (self.dealer_pos + 2)%len(self.players) and
                                    len(players_acted_this_betting_level) >= len([p for p in self.players if not p.is_folded and not p.is_all_in]) -1
                                   )

            if all_eligible_acted and all_bets_equalized and not is_preflop_bb_option:
                round_over = True
            
            if is_preflop_bb_option and (action == "check" or action == "call"):
                round_over = True
            
            if not round_over:
                 self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            
            actions_this_round += 1
            if actions_this_round > len(self.players) * 3:
                break

    def _showdown(self):
        self.game_state = "showdown"
        self.message = "Showdown"
        
        eligible_players = [p for p in self.players if not p.is_folded]
        if not eligible_players:
            return

        if len(eligible_players) == 1:
            winner = eligible_players[0]
            self.message = f"{winner.name} wins {self.pot} uncontested"
            winner.chips += self.pot
            return

        best_hand_tuples = []
        self.showdown_info = []
        for player in eligible_players:
            combined_cards = player.hole_cards + self.board
            rank_code, tie_breakers, best_5_cards = self.evaluator.get_best_hand(combined_cards)
            best_hand_tuples.append((player, rank_code, tie_breakers, best_5_cards))
            self.showdown_info.append(
                f"{player.name}: {HAND_RANK_NAMES[rank_code]} ({[str(c) for c in best_5_cards]})"
            )

        winners = []
        best_seen_rank_tuple_for_comparison = (HIGH_CARD, [-1], [])

        for p_tuple in best_hand_tuples:
            player_obj, rank_c, tb_vals, _ = p_tuple
            current_eval_tuple = (rank_c, tb_vals, [])

            if not winners:
                winners = [player_obj]
                best_seen_rank_tuple_for_comparison = current_eval_tuple
            else:
                comparison_result = self.evaluator._compare_rank_tuples(current_eval_tuple, best_seen_rank_tuple_for_comparison)
                if comparison_result > 0:
                    winners = [player_obj]
                    best_seen_rank_tuple_for_comparison = current_eval_tuple
                elif comparison_result == 0:
                    winners.append(player_obj)
        
        if winners:
            pot_per_winner = self.pot / len(winners)
            win_names = ", ".join([w.name for w in winners])
            self.message = f"Winner(s): {win_names}, each gets {pot_per_winner:.2f} chips"
            for winner in winners:
                winner.chips += pot_per_winner
        else:
            self.message = "Error: No winner determined"

    def play_hand(self):
        if len([p for p in self.players if p.chips > 0]) < 2:
            self.message = "Not enough players with chips"
            return False

        self.deck = Deck()
        self.board = []
        self.pot = 0
        self.current_street_highest_bet = 0
        self.equity_display = ""
        self.showdown_info = []
        for p in self.players:
            p.reset_for_hand()
        
        self._rotate_dealer()
        self.message = f"New Hand - Dealer: {self.players[self.dealer_pos].name}"

        if not self._post_blinds():
            return False
        self._deal_hole_cards()

        # Pre-flop betting
        self.game_state = "pre_flop"
        self._betting_round("Pre-flop")
        if len([p for p in self.players if not p.is_folded]) <= 1:
            self._showdown()
            return True

        # Flop
        self.board.extend(self.deck.deal(3))
        self.game_state = "flop"
        self.message = "Flop Dealt"
        self._betting_round("Flop")
        if len([p for p in self.players if not p.is_folded]) <= 1:
            self._showdown()
            return True

        # Turn
        self.board.append(self.deck.deal())
        self.game_state = "turn"
        self.message = "Turn Dealt"
        self._betting_round("Turn")
        if len([p for p in self.players if not p.is_folded]) <= 1:
            self._showdown()
            return True

        # River
        self.board.append(self.deck.deal())
        self.game_state = "river"
        self.message = "River Dealt"
        self._betting_round("River")
        self._showdown()
        return True

    def play_game(self, num_hands=5):
        for hand_num in range(num_hands):
            if not self.play_hand():
                break
            
            # Show results for a few seconds
            for _ in range(150):  # About 5 seconds
                self.draw()
                pygame.display.flip()
                pygame.time.delay(33)
                
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
            
            # Remove players with no chips
            self.players = [p for p in self.players if p.chips > 0]
            if len(self.players) < 2:
                break
                
        # Show final results
        self.message = "Game Over"
        self.game_state = "game_over"
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            
            self.draw()
            pygame.display.flip()
            pygame.time.delay(33)

    def draw(self):
        # Fill background
        screen.fill(BACKGROUND_COLOR)
        
        # Draw table
        pygame.draw.circle(screen, (0, 70, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 300)
        pygame.draw.circle(screen, (0, 90, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 280, 5)
        
        # Draw pot
        pot_text = FONT_LARGE.render(f"Pot: {self.pot}", True, TEXT_COLOR)
        screen.blit(pot_text, (SCREEN_WIDTH//2 - pot_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
        
        # Draw dealer button
        if self.dealer_pos >= 0 and self.dealer_pos < len(self.players):
            dealer_x, dealer_y = self.players[self.dealer_pos].position
            pygame.draw.circle(screen, (255, 255, 255), (dealer_x, dealer_y - 70), 15)
            dealer_text = FONT_SMALL.render("D", True, (0, 0, 0))
            screen.blit(dealer_text, (dealer_x - dealer_text.get_width()//2, dealer_y - 70 - dealer_text.get_height()//2))
        
        # Draw community cards
        if self.board:
            board_x = SCREEN_WIDTH//2 - (len(self.board) * (CARD_WIDTH + CARD_SPACING)) // 2
            board_y = SCREEN_HEIGHT//2 - CARD_HEIGHT//2
            
            for i, card in enumerate(self.board):
                card.draw(screen, board_x + i*(CARD_WIDTH + CARD_SPACING), board_y)
        
        # Draw players
        for i, player in enumerate(self.players):
            x, y = player.position
            is_active = (i == self.current_player_idx and 
                         not player.is_folded and 
                         not player.is_all_in and
                         "game_over" not in self.game_state)
            player.draw(screen, x - 100, y - 50, is_active)
            
            # Draw chips in front of player
            chip_x = x - 20
            chip_y = y + 30
            if player.current_bet_in_street > 0:
                pygame.draw.circle(screen, CHIP_COLORS['white'], (chip_x, chip_y), 15)
                bet_text = FONT_SMALL.render(str(player.current_bet_in_street), True, (0, 0, 0))
                screen.blit(bet_text, (chip_x - bet_text.get_width()//2, chip_y - bet_text.get_height()//2))
        
        # Draw message
        if self.message:
            msg_surf = FONT_LARGE.render(self.message, True, TEXT_COLOR)
            screen.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, 20))
        
        # Draw equity display
        if self.equity_display:
            equity_surf = FONT_MEDIUM.render(self.equity_display, True, (200, 200, 100))
            screen.blit(equity_surf, (SCREEN_WIDTH - equity_surf.get_width() - 20, SCREEN_HEIGHT - 100))
        
        # Draw showdown info
        if self.showdown_info:
            for i, info in enumerate(self.showdown_info):
                info_surf = FONT_MEDIUM.render(info, True, (255, 255, 200))
                screen.blit(info_surf, (SCREEN_WIDTH//2 - info_surf.get_width()//2, 60 + i*30))
        
        # Draw game state
        state_surf = FONT_MEDIUM.render(f"Phase: {self.game_state.upper()}", True, (200, 200, 200))
        screen.blit(state_surf, (20, 20))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
            
        # Draw game over message
        if self.game_state == "game_over":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_surf = FONT_TITLE.render("GAME OVER", True, (255, 215, 0))
            screen.blit(game_over_surf, (SCREEN_WIDTH//2 - game_over_surf.get_width()//2, SCREEN_HEIGHT//2 - 50))
            
            # Show final chip counts
            for i, player in enumerate(self.players):
                chip_text = FONT_LARGE.render(f"{player.name}: {player.chips} chips", True, TEXT_COLOR)
                screen.blit(chip_text, (SCREEN_WIDTH//2 - chip_text.get_width()//2, SCREEN_HEIGHT//2 + i*40))
            
            restart_text = FONT_MEDIUM.render("Press ESC to exit", True, (200, 200, 200))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT - 50))

# Main game execution
if __name__ == "__main__":
    # Setup players (name, starting_chips) - First player is human
    player_config = [
        ("You", 1000),
        ("Mumbaka", 1000),
        ("John", 1000),
        ("Bob", 1000),
        ("Boolakapa", 1000),
        ("Beta", 1000)
    ]
    
    game = TexasHoldemGame(player_config, small_blind=50, big_blind=75)
    game.play_game(num_hands=20)