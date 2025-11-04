using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Runtime;
using System.Security;
using System.Transactions;
using System.Threading;

namespace TextAdventure
{
    class Game
    {
        // ? gets rid of null warnings
        public Player? Player { get; private set; }
        public Room? CurrentRoom { get; private set; }

        private Dictionary<string, Room> rooms = new();

        public void Start()
        {
            Console.WriteLine($"You are a loyal member of the Royal Guard.\n"
                + $"A violent coup has plunged the palace into chaos, \n"
                + $"and the royal family has been dethroned.\n"
                + $"As far as you know, the Prince is the only survivor.");
            Console.Write("Enter your name, brave guard: ");
            string name = Console.ReadLine();
            Player = new Player(name);

            SetUpWorld();

            Console.WriteLine("\n=================================\n");
            Console.WriteLine($"\nWelcome, {Player.Name}. The Prince is being held somewhere in the Castle. You must find him!");
            CurrentRoom.Enter();

            GameManager gameManager = new GameManager(this);
            gameManager.Run();
        }

        public void SetUpWorld()
        {

            // sets up the rooms
            var courtyard = new Room("Courtyard", "You stand in the moonlit courtyard of the Castle.");
            var armory = new Room("Armory", "Racks of weapons and armor line the walls. Or at least they used to. The insurgants must be well armed now.");
            var dungeon = new Room("Dungeon", "Dark, cold, and damp. You hope the Prince is somewhere more comfortable.");
            var corridor = new Room("Corridor", "The corridor leads to the throne room. You always told your captain that it would be hard to defend during an attack. Too little cover. You think the bodies lying in the open prove you right.");
            var throneRoom = new Room("Throne Room", "A grand chamber with a now red carpet. You think it used to be white");
            var royalChamber = new Room("Royal Chamber", "The final door. You hope the Prince is here.");
            var kitchen = new Room("Kitchen", "A good place to resupply");

            //sets the royal chamber as the final room
            royalChamber.IsFinalRoom = true;

            // connect the rooms
            courtyard.Exits["north"] = armory;
            armory.Exits["south"] = courtyard;

            courtyard.Exits["east"] = corridor;
            corridor.Exits["west"] = courtyard;

            corridor.Exits["north"] = throneRoom;
            throneRoom.Exits["south"] = corridor;

            corridor.Exits["down"] = dungeon;
            dungeon.Exits["up"] = corridor;

            throneRoom.Exits["up"] = royalChamber;
            royalChamber.Exits["down"] = throneRoom;

            // fill the rooms with items
            armory.Items.Add(new Weapon("Iron Sword", "A little dull. Cracked at the edges, you think you know why the insurgents left it.","A dull sword lies abandoned in the corner." ,10));
            dungeon.Items.Add(new HealthPotion());
            throneRoom.Items.Add(new Key());
            corridor.Items.Add(new Armor("Iron Cuirass", "It has a hole in the side.", "It glints in the candlelight. You could pull it off the body of your former colleague.", 20));
            corridor.Items.Add(new Weapon("Steel Dagger", "A sharp steel dagger.", "All you can see is the blood-soaked handle. You hope it will still be intact after you pull it from the corpse.", 8));

            // populate enemies
            dungeon.Enemy = new Bandit();
            throneRoom.Enemy = new Sorcerer();

            // store room variables
            rooms["courtyard"] = courtyard;
            rooms["armory"] = armory;
            rooms["dungeon"] = dungeon;
            rooms["throneroom"] = throneRoom;
            rooms["royalchamber"] = royalChamber;

            // start at the courtyard
            CurrentRoom = courtyard;

            //lock the door to the royal chamber
            royalChamber.Locked = true;
            royalChamber.RequiredKeyName = "Key";

        }

        public void Move(string direction)
        {
            //stops the player from retreating from the final boss
            if (CurrentRoom.IsFinalRoom)
            {
                Console.WriteLine("There's no turning back now. This is the final act.");
                return;
            }

            if (CurrentRoom.Exits.ContainsKey(direction))
            {
                var nextRoom = CurrentRoom.Exits[direction];

                if (nextRoom.Locked)
                {
                    Console.WriteLine("The door is locked. You need a key to open it.");
                    return;
                }
                CurrentRoom = nextRoom;
                CurrentRoom.Enter();

                if (CurrentRoom.IsFinalRoom)
                {
                    TriggerFinalAct();
                }
            }
            else
            {
                Console.WriteLine("You can't go that way.");
            }

        }

        private void Pause(int milliseconds = 1500)
        {
            Thread.Sleep(milliseconds);
        }

        private void TriggerFinalAct()
        {
            Console.WriteLine("\nYou climb the stairs to the royal chamber, hoping against hope that the Prince is safe.");
            Pause();
            Console.WriteLine("As you mount the final steps, a shadowy figure blocks your path.");
            Pause();
            Console.WriteLine($"'{Player.Name}...' The shadowy figure growls. He takes a step forward, his broadsword's tip dragging against the ground.");
            Pause();
            Console.WriteLine("'You have finally come.' He raises his sword, the same one that took the lives the the King and Queen, and levels it at your chest.");
            Pause();
            Console.WriteLine("'I wondered when you would come save your precious Prince. You were always the most loyal of us. Following their every whim like a dog,'");
            Console.WriteLine("He snarls.");

            var finalBoss = new FinalBoss("Traitor", 80, 12);

            finalBoss.Loot.Add(
                new Weapon("Knight's Broadsword", "The murderous blade the killed the Kind and Queen", "It gleams in the soft light case by the moon. It's beautiful, but you can't help but remember what it has done.", 30)
            );

            CurrentRoom.Enemy = finalBoss;
        }

        public void TriggerEnding()
        {
            Console.WriteLine("\nAs the final blow lands, the Traitor collapses to his knees.");
            Pause();
            Console.WriteLine("His blade clatters to the floor, echoing through the mostly silent chamber.");
            Pause();
            Console.WriteLine("As the light fades from his eyes, you look past him and see the Prince, beaten, bound, and gagged, but alive. Blessedly alive.");
            Pause();
            Console.WriteLine("You rush to him and cut his bonds. As the gag falls out of his mouth, he utters his quiet thanks, voice hoarse from disuse.");
            Pause();
            Console.WriteLine("You help him to his feet. The two of you stand in amidst the wreckage of your kingdom.");
            Pause();
            Console.WriteLine("For the first time since this all began, you feel hope. There are many more enemies that need killing,");
            Pause();
            Console.WriteLine("But with the rescue of the Prince and the slaying of the traitor, you have dealt a serious blow to the enemy.");

            Pause();
            Pause();
            Console.WriteLine("=====================================");
            Console.WriteLine("              THE END                ");
            Console.WriteLine("=====================================");
            Console.WriteLine("\nPress Enter to exit...");
            Console.ReadLine();
        
        }
    }
}