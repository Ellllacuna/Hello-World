using System.Security;

abstract class Enemy
{
    public string Name { get; }
    public int Health { get; set; }
    public int AttackPower { get; }

    // loot that the enemy drops
    public List<Item> Loot { get; } = new();

    public Enemy(string name, int health, int attackPower)
    {
        Name = name;
        Health = health;
        AttackPower = attackPower;
    }

    public abstract void Attack(Player player);
}

class Bandit : Enemy
{
    public Bandit() : base("Bandit", 30, 5)
    {
        //adds loot that the enemy will drop
        Loot.Add(new Weapon("Rusty Dagger", "Looks like it won't last another hit", "The dagger the bandit used now lies abandoned on the floor", 3));
        Loot.Add(new HealthPotion("Health Potion", "Restores 30 HP.", "A small red vial from the bandit's pocket.", 30));
        Loot.Add(new HealthPotion("Meat", "Some sort of mystery meat", "The bandit has food in their pocket.", 5));
        Loot.Add(new HealthPotion("Apple", "A bruised apple.", "The bandit has food in their pocket.",5));
    }

    public override void Attack(Player player)
    {
        Console.WriteLine("The bandit slashes at you!");
        player.Health -= AttackPower;
    }
}

class Sorcerer : Enemy
{
    public Sorcerer() : base("Sorcerer", 40, 8)
    {
        Loot.Add(new Armor("Steel Gauntlets", "Slightly bloody, but in good condition.", "You could take the sorcerer's gloves. He deserves it.", 5));
        Loot.Add(new Weapon("Quarterstaff", "You can't use magic, but the enchantment on this staff increases your strength.", "The sorcerer's staff lies a distance away from his body.", 20));
        Loot.Add(new HealthPotion("Health Potion", "Restores 30 HP.", "A small red vial from the sorcerer's pocket.", 30));
    }

    public override void Attack(Player player)
    {
        Console.WriteLine("The sorcerer casts a bolt of lightning!");
        player.Health -= AttackPower;
    }
}

class FinalBoss : Enemy
{
    public FinalBoss(string name, int health, int attackPower) : base(name, health, attackPower) { }

    public override void Attack(Player player)
    {
        Console.WriteLine($"The {Name} swings his massive sword at you.");
        player.Health -= AttackPower;
    }
}
