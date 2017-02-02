#include <display.hpp>
#include <iostream>

Display::Display() {
    // yes, this is a bit of a hack, but it works and
    // wiringPi can't turn on the display
    system("python init_display.py");

    mcp23017Setup(AF_BASE, 0x20);
    this->lcd = lcdInit(2, 16, 4, AF_RS, AF_E, AF_DB4,
            AF_DB5, AF_DB6, AF_DB7, 0, 0, 0, 0);
    this->cursor_row = 0;
    this->cursor_col = 0;
    lcdDisplay(this->lcd, true);
    lcdHome(this->lcd);
    lcdClear(this->lcd);
    for (int row = 0; row < NUM_ROWS; ++row) {
        for (int col = 0; col < NUM_COLS; ++col) {
            curr_text[row][col] = ' ';
        }
    }
    this->clear();
}

void Display::clear() {
    for (int row = 0; row < NUM_ROWS; ++row) {
        for (int col = 0; col < NUM_COLS; ++col) {
            new_text[row][col] = ' ';
        }
    }
    this->update();
}

void Display::update() {
    for (int row = 0; row < NUM_ROWS; ++row) {
        for (int col = 0; col < NUM_COLS; ++col) {
            // only update if changed
            if (this->curr_text[row][col] != this->new_text[row][col]) {
                this->curr_text[row][col] = this->new_text[row][col];
                lcdPosition(this->lcd, col, row);
                lcdPutchar(this->lcd, this->curr_text[row][col]);
            }
        }
    }
    lcdPosition(this->lcd, this->cursor_col, this->cursor_row);
}

void Display::message(std::string message) {
    this->clear();
    int row = 0;
    int col = 0;
    for (char c : message) {
        if (c == '\n' || col >= NUM_COLS) {
            row++;
            col = 0;
            continue;
        } else if (row >= NUM_ROWS) {
            break;
        }
        this->new_text[row][col] = c;
        col++;
    }
    this->update();
}

void Display::set_row(std::string text, int row) {
    // TODO implement
}

void Display::set_char(char c, int row, int col) {
    // TODO implement
}

void Display::set_cursor_position(int row, int col) {
    this->cursor_row = row;
    this->cursor_col = col;
    lcdPosition(this->lcd, this->cursor_col, this->cursor_row);
}

void Display::set_cursor_enabled(bool val) {
    this->cursor_enabled = val;
    lcdCursor(this->lcd, val);
}

void Display::set_cursor_blink_enabled(bool val) {
    this->cursor_blink_enabled = val;
    lcdCursorBlink(this->lcd, val);
}

