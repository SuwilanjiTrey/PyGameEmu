-- game.lua
math.randomseed(os.time())

local target = math.random(1, 100)

function guess_number(guess)
    if guess == target then
        return "Correct! You've guessed the number!"
    elseif guess < target then
        return "Too low! Try again."
    else
        return "Too high! Try again."
    end
end

function reset_game()
    target = math.random(1, 100)
    return "The game has been reset. Guess the new number!"
end
