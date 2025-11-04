using System.Reflection.Metadata;
using System.Runtime.CompilerServices;

abstract class Item
{
    public string Name { get; }
    public string Description { get; }
    //description for where the item is when you first see it
    public string RoomDescription { get;  }

    public Item(string name, string description, string roomDescription)
    {
        Name = name;
        Description = description;
        RoomDescription = roomDescription;
    }

    // method to use items
    public abstract void Use(Player player);
}

// subclasses for items

class HealthPotion : Item
{
    // inits health potion, restores 10 health
    public HealthPotion() : base("Health Potion", "Restores 30 HP.", "A small red vial rests on the table.") { }

    public override void Use(Player player)
    {
        Console.WriteLine("You drink the potion and feel rejuvenated.");
        player.Health += 30;
        player.Inventory.Remove(this);
    }
}

class Key : Item
{
    public Key() : base("Key", "Not an ordinary Key", "An ornate looking key hangs from the belt of your former captain. You can't look him in the face.") { }

    // using the key without a door context
    public override void Use(Player player)
    {
        var game = GameManager.CurrentGame;
        var currentRoom = game.CurrentRoom;

        foreach (var exit in currentRoom.Exits.Values)
        {
            if (exit.Locked && exit.RequiredKeyName == Name)
            {
                exit.Locked = false;
                Console.WriteLine("The key fits in the lock. It clicks open.");
                return;
            }
        }
        Console.WriteLine("You hold the key tightly. It might open something important.");
    }
}

class Weapon : Item
{
    public int Damage { get; }
    public Weapon(string name, string description, string roomDescription, int damage) : base(name, description, roomDescription)
    {
        Damage = damage;
    }

    public override void Use(Player player)
    {
        player.EquipWeapon(this);
    }
}

class Armor : Item
{
    public int Defense { get; }

    public Armor(string name, string description, string roomDescription, int defense) : base(name, description, roomDescription)
    {
        Defense = defense;
    }

    public override void Use(Player player)
    {
        Console.WriteLine($"You equip the {Name}. Your Health increases by {Defense}.");
        player.Health += Defense;
        player.EquippedArmor.Add(this);
    }
}