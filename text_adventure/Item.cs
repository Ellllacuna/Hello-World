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
//can be used for health potions or for food
{
    public int Restoration { get; }
    public HealthPotion(string name, string description, string roomDescription, int restoration) : base(name, description, roomDescription)
    {
        Restoration = restoration;
    }

    public override void Use(Player player)
    {
        //if the item heals or hurts you
        if (Restoration >= 0)
        {
            Console.WriteLine($"You use the {Name} and feel rejuvenated. You restore {Restoration} HP.");
        }
        else
        {
            Console.WriteLine($"You use the {Name} and feel... bad. It hurts you. You lose {-Restoration} HP.");
        }
        player.Health += Restoration;
        player.Inventory.Remove(this);
    }
}

class BuffItem : Item
{
    public int DamageBuff { get; }
    public int Duration { get; }
    public BuffItem(string name, string description, string roomDescription, int damageBuff, int duration = 2) : base(name, description, roomDescription)
    {
        DamageBuff = damageBuff;
        Duration = duration;
    }
    public override void Use(Player player)
    {
        //gives damage buff to a specific item, not to the player itself
        var weapon = player.EquippedWeapon;

        if (weapon != null)
        {
            weapon.ApplyBuff(DamageBuff, Duration);
            Console.WriteLine($"{weapon.Name}'s damage has increased. It won't last forever.");
            player.Inventory.Remove(this);
        }
        else
        {
            Console.WriteLine("You can't use this item on your hands.");
        }
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
    public int Damage { get; set; }
    //for damage buffs
    public int? TemporaryBuff { get; private set; } = null;
    public int? BuffBattleTimer { get; private set; } = null;
    public Weapon(string name, string description, string roomDescription, int damage) : base(name, description, roomDescription)
    {
        Damage = damage;
    }

    public override void Use(Player player)
    {
        player.EquipWeapon(this);
    }

    //for applying a temorary buff to items
    public void ApplyBuff(int buffAmount, int battleCount)
    {
        TemporaryBuff = buffAmount;
        BuffBattleTimer = battleCount;
        Damage += buffAmount;
    }

    public void BuffBattleCountdown()
    {
        if (BuffBattleTimer > 0)
        {
            BuffBattleTimer--;
            if (BuffBattleTimer == 0 && TemporaryBuff.HasValue)
            {
                Damage -= TemporaryBuff.Value;
                TemporaryBuff = null;
                Console.WriteLine("The item has lost it's potency.");
            }
        }
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