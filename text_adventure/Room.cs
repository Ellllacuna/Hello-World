using System.Runtime.CompilerServices;

class Room
{
    public string Name { get; }
    public string Description { get; }
    public Dictionary<string, Room> Exits { get; } = new();
    public List<Item> Items { get; } = new();
    public List<Enemy> Enemies { get; set; } = new List<Enemy>();

    //for the locked door
    public bool Locked { get; set; } = false;
    public string? RequiredKeyName { get; set; }

    // used for triggering final scene. In this case, the royal chamber
    public bool IsFinalRoom { get; set; } = false;

    public Room(string name, string description)
    {
        Name = name;
        Description = description;
    }

    public virtual void Enter()
    {
        Console.WriteLine($"\n== {Name} ==");
        Console.WriteLine(Description);
        Console.WriteLine();
        if (Items.Count > 0)
        {
            foreach (var item in Items)
            {
                Console.WriteLine($"You see: {item.Name} - {item.RoomDescription}");
            }
            Console.WriteLine();
        }
        if (Enemies.Count > 0)
        {
            foreach (var enemy in Enemies)
            {
                Console.WriteLine($"An enemy appears: {enemy.Name}\n    (HP: {enemy.Health})");
                Console.WriteLine();
            }
            Console.WriteLine();
        }

        if (Exits.Count > 0)
        {
            //exit is an entry in the Exits dictionary, refers to the key value pair of direction and room
            var exitDescriptions = Exits.Select(exit =>
            {
                string direction = exit.Key;
                Room room = exit.Value;

                if (direction == "up" || direction == "down")
                {
                    return $"a staircase going {direction}";
                }
                else
                {
                    return $"a door to the {direction}";
                }
            });

            Console.WriteLine("You see " + string.Join(" and ", exitDescriptions) + ".");
        }
    }
}


//planned to use these, but didn't
class TrapRoom : Room
{
    public TrapRoom(String name, string description) : base(name, description) { }

    public override void Enter()
    {
        base.Enter();
        Console.WriteLine("A hidden trap triggers! You loose some health.");
    }
}

class TreasureRoom : Room
{
    public TreasureRoom(String name, string description) : base(name, description) { }

    public override void Enter()
    {
        base.Enter();
        Console.WriteLine("You spot a shimmering chest filled with loot!");
    }
}