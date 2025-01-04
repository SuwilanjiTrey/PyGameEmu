-- simple_game.lua

function love.load()
    love.window.setTitle("Simple Love2D Game")
    love.graphics.setBackgroundColor(0.2, 0.3, 0.4)
    player = { x = 400, y = 300, speed = 200 }
end

function love.update(dt)
    if love.keyboard.isDown("left") then
        player.x = player.x - player.speed * dt
    end
    if love.keyboard.isDown("right") then
        player.x = player.x + player.speed * dt
    end
    if love.keyboard.isDown("up") then
        player.y = player.y - player.speed * dt
    end
    if love.keyboard.isDown("down") then
        player.y = player.y + player.speed * dt
    end
end

function love.draw()
    love.graphics.setColor(1, 1, 1)
    love.graphics.circle("fill", player.x, player.y, 25)
end
