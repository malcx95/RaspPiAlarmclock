#ifndef BUTTONS_H
#define BUTTONS_H

#include <vector>

namespace buttons {

    enum Button {

        ENTER = 11,
        LEFT  = 13,
        RIGHT = 15,
        BACK  = 29,
        KEY1  = 31,
        KEY2  = 33,
        KEY3  = 35,
        KEY4  = 37
    
    };

    void buttons_init();

    bool is_pressed(const Button b);

    const std::vector<Button> ALL_BUTTONS {
        ENTER, LEFT, RIGHT, BACK, KEY1, KEY2, KEY3, KEY4 
    };

};

#endif /* ifndef BUTTONS_H */


