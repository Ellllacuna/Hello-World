using System;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Runtime.CompilerServices;
using TextAdventure;
class GameManager
{
    public static Game? CurrentGame { get; private set; }
    private Game game;
    private bool isRunning = true;

    Random random = new Random();

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
        // if the command has no second part, it assigns it a blank string as argument, otherwise is just parts[1]
        string argument = parts.Length > 1 ? parts[1] : "";

        //like an if-else statement. give it a list of cases, and which code to execute
        switch (command)
        {
            case "look":
                game.CurrentRoom.Enter();
                break;

            case "go":
            case "walk":
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
            case "grab":
                TakeItem(argument);
                break;

            case "inventory":
            case "bag":
                game.Player.ShowInventory();
                break;

            case "use":
            case "equip":
            case "eat":
                UseItem(argument);
                break;

            case "attack":
                AttackEnemy(argument);
                break;

            case "quit":
                isRunning = false;
                Console.WriteLine("You have abandoned the Prince.");
                break;

            case "stats":
            case "statistics":
            case "player":
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

    private void AttackEnemy(string targetName)
    {
        var enemies = game.CurrentRoom.Enemies;

        if (enemies.Count == 0)
        {
            Console.WriteLine("There's no one here to fight.");
            return;
        }

        //returns the first enemy in the list that matches the conditions (in this case, matches the targetName)
        //allows the player to specify which enemy they want to attack
        Enemy? targetEnemy = enemies.FirstOrDefault(e => e.Name.Equals(targetName, StringComparison.OrdinalIgnoreCase));

        if (targetEnemy == null)
        {
            Console.WriteLine($"There's no {targetName} here");
            return;
        }

        Console.WriteLine($"You attack the {targetEnemy.Name}.");
        targetEnemy.Health -= game.Player.AttackPower;

        //enemy dead
        if (targetEnemy.Health <= 0)
        {
            Console.WriteLine();
            Console.WriteLine($"You defeated the {targetEnemy.Name}. One less enemy in your path.");
            //if the player has an item with a damage buff equiped, decrements the battle counter
            if (game.Player.EquippedWeapon != null)
            {
                game.Player.EquippedWeapon.BuffBattleCountdown();
            }

            if (targetEnemy.Loot.Count > 0)
            {
                Console.WriteLine($"The {targetEnemy.Name} dropped:");
                // foreach (var item in enemy.Loot)
                // {
                //     Console.WriteLine($"- {item.Name}");
                //     game.CurrentRoom.Items.Add(item);
                // }
                int numDrops = random.Next(1, targetEnemy.Loot.Count + 1);
                var randomizedLoot = targetEnemy.Loot.OrderBy(x => random.Next()).Take(numDrops).ToList();

                foreach (var item in randomizedLoot)
                {
                    Console.WriteLine($"- {item.Name}");
                    game.CurrentRoom.Items.Add(item);
                }
                
            }

            if (targetEnemy is FinalBoss)
            {
                game.TriggerEnding();
                return;
            }
            enemies.Remove(targetEnemy);

            if (enemies.Count == 0)
            {
                Console.WriteLine("All enemies in this room have been defeated.");
            }
        }
        else
        {
            targetEnemy.Attack(game.Player);
            Console.WriteLine($"Your HP: {game.Player.Health}");
        }
    }

    private void ShowStats()
    {
        Console.WriteLine($"Health: {game.Player.Health}");
        Console.WriteLine($"Attack Power: {game.Player.AttackPower}");

        if (game.Player.EquippedWeapon != null)
        {
            var weapon = game.Player.EquippedWeapon;
            //shows the temporary buff if the player has any
            if (weapon.TemporaryBuff > 0 && weapon.BuffBattleTimer > 0)
            {
                Console.WriteLine($"Item Buff: +{weapon.TemporaryBuff} Attack Power");
                Console.WriteLine($"Buff Duration: {weapon.BuffBattleTimer} Battles");
            }
        }
    }
}