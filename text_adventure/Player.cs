class Player
{
    public string Name { get; }
    // player health is set at a base of 30
    public int Health { get; set; } = 30;
    // player attack power is set at a base of 5
    public int BaseAttackPower { get; } = 5;
    public int AttackPower { get;  private set; }
    // list of items in player inventory
    public List<Item> Inventory { get; } = new();

    // currently equipped weapon. Makes sure the play can only equip one weapon at a time
    public Weapon? EquippedWeapon { get; private set; }
    public List<Armor> EquippedArmor { get; } = new();

    public Player(string name)
    {
        Name = name;
        //starts attack power at 5, allows me to add attack power in the future
        AttackPower = BaseAttackPower;
    }

    public void EquipWeapon(Weapon weapon)
    {
        if (EquippedWeapon != null)
        {
            //removes old weapon's damage
            AttackPower -= EquippedWeapon.Damage;
            Console.WriteLine($"You unequip the {EquippedWeapon.Name}.");
        }
        //replaces old weapon with new
        EquippedWeapon = weapon;
        AttackPower += weapon.Damage;
        Console.WriteLine($"You equip the {weapon.Name}. Your attack power is now {AttackPower}.");
    }


    public void ShowInventory()
    {
        if (Inventory.Count == 0)
        {
            Console.WriteLine("Your inventory is empty.");
        } else
        {
            Console.WriteLine("You are carrying:");
            foreach (var item in Inventory)
            {
                string prefix = "-";
                if (item == EquippedWeapon || (item is Armor a && EquippedArmor.Contains(a)))
                {
                    prefix = "*";
                }
                Console.WriteLine($"{prefix} {item.Name}: {item.Description}");
            }
        }
    }
}