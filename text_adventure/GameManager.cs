using System;
using System.Linq;
using TextAdventure;

class GameManager
{
    public static Game CurrentGame { get; private set; }
    private Game game;
    private bool isRunning = true;

    public GameManager(Game game)
    {
        this.game = game;
        CurrentGame = game;
    }

    public void Run()
    {
        while (isRunning && game.Player.Health > 0)
        {
            Console.Write("\n");
            string input = Console.ReadLine().Trim().ToLower();
            HandleCommand(input);
        }

        if (game.Player.Health <= 0)
        {
            Console.WriteLine("You have fallen in battle. The Prince remains captive...");

        }
    }

    private void HandleCommand(string input)
    {
        //splits the command into two parts (eg. "go" , "north room")
        string[] parts = input.Split(' ', 2);
        // the first part is the command (eg. "go","look" ect..)
        string command = parts[0];
        // if the command has no second part, it assigns it a blank string as argument
        string argument = parts.Length > 1 ? parts[1] : "";

        //like an if-else statement. give it a list of cases, and which code to execute
        switch (command)
        {
            case "look":
                game.CurrentRoom.Enter();
                break;

            case "go":
                // if they just said to go, asks where. can't go with no direction
                if (argument == "")
                {
                    Console.WriteLine("Go where?");
                }
                else
                {
                    game.Move(argument);
                }
                break;

            case "take":
                TakeItem(argument);
                break;

            case "inventory":
                game.Player.ShowInventory();
                break;

            case "use":
                UseItem(argument);
                break;

            case "attack":
                AttackEnemy();
                break;

            case "quit":
                isRunning = false;
                Console.WriteLine("You have abandoned the Prince.");
                break;

            case "stats":
                ShowStats();
                break;

            default:
                Console.WriteLine("Unknown Command.");
                break;
        }
    }

    private void TakeItem(string itemName)
    {
        //returns the items in the current room. FirstOrDefault returns either the first item, or null if there is nothing
        var item = game.CurrentRoom.Items.FirstOrDefault(i => i.Name.ToLower() == itemName);
        if (item == null)
        {
            Console.WriteLine("That item isn't here.");
            return;
        }

        game.Player.Inventory.Add(item);
        game.CurrentRoom.Items.Remove(item);
        Console.WriteLine($"You picked up {item.Name}: {item.Description}");

    }

    private void UseItem(string itemName)
    {
        var item = game.Player.Inventory.FirstOrDefault(i => i.Name.ToLower() == itemName);
        if (item == null)
        {
            Console.WriteLine("You don't have that item.");
            return;
        }

        item.Use(game.Player);
    }

    private void AttackEnemy()
    {
        var enemy = game.CurrentRoom.Enemy;
        if (enemy == null)
        {
            Console.WriteLine("There's no one here to fight.");
            return;
        }

        Console.WriteLine($"You attack the {enemy.Name}.");
        enemy.Health -= game.Player.AttackPower;

        //enemy dead
        if (enemy.Health <= 0)
        {
            Console.WriteLine($"You defeated the {enemy.Name}. One less enemy in your path.");

            if (enemy.Loot.Count > 0)
            {
                Console.WriteLine($"The {enemy.Name} dropped:");
                foreach (var item in enemy.Loot)
                {
                    Console.WriteLine($"- {item.Name}");
                    game.CurrentRoom.Items.Add(item);
                }
            }

            if (enemy is FinalBoss)
            {
                game.TriggerEnding();
                return;
            }
            game.CurrentRoom.Enemy = null;
        }
        else
        {
            enemy.Attack(game.Player);
            Console.WriteLine($"Your HP: {game.Player.Health}");
        }
    }

    private void ShowStats()
    {
        Console.WriteLine($"Health: {game.Player.Health}");
        Console.WriteLine($"Attack Power: {game.Player.AttackPower}");
    }
}