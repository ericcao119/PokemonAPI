CREATE TABLE IF NOT EXISTS Species (
  pokemon_id INTEGER PRIMARY KEY AUTOINCREMENT,
  species_name TEXT NOT NULL,
  variant_name TEXT NOT NULL,
  primary_type TEXT NOT NULL,
  secondary_type TEXT NOT NULL,
  hp INT NOT NULL,
  attack INT NOT NULL,
  defense INT NOT NULL,
  speed INT NOT NULL,
  special_attack INT NOT NULL,
  special_defense INT NOT NULL,

  /* Dex Numbers and Information */
  national_dex_num INT NOT NULL,
  rby_dex_num INT,
  gsc_dex_num INT,
  rse_dex_num INT,
  frlg_dex_num INT,
  dp_dex_num INT,
  plat_dex_num INT,
  hgss_dex_num INT,
  bw_dex_num INT,
  b2w2_dex_num INT,
  xy_central_dex_num INT,
  xy_coastal_dex_num INT,
  xy_mountain_dex_num INT,
  oras_dex_num INT,
  sm_dex_num INT,
  usum_dex_num INT,
  lets_go_dex_num INT,
  swsh_dex_num INT,


  height_meters FLOAT,
  weight_kilos FLOAT,
  color TEXT,
  shape TEXT,
  kind TEXT,
  flavor_text TEXT,

  /* Training Information */
  leveling_rate TEXT,
  base_exp_yield INT,
  effort_hp INT,
  effort_attack INT,
  effort_defense INT,
  effort_speed INT,
  effort_special_attack INT,
  effort_special_defense INT,
  catch_rate INT,
  base_friendship INT,
  
  /* Breeding Information */
  primary_egg_group TEXT,
  secondary_egg_group TEXT,
  male_rate FLOAT,
  steps_to_hatch_lower INT,
  steps_to_hatch_upper INT,
  egg_cycles INT,

  UNIQUE (species_name, variant_name) ON CONFLICT REPLACE
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_species ON Species (species_name, variant_name);

-- Evolutions stored in json

-- Ability Table
CREATE TABLE IF NOT EXISTS Ability (
  ability_id INTEGER PRIMARY KEY AUTOINCREMENT,
  ability_name TEXT UNIQUE,
  effect TEXT,
  description TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_ability_name ON Ability (ability_name);

CREATE TABLE IF NOT EXISTS PokemonWithAbility (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pokemon_id INT, -- FOREIGN KEY
  ability_id INT, -- FOREIGN KEY

  ability_index INT NOT NULL,
  is_hidden BOOLEAN NOT NULL,

  UNIQUE (pokemon_id, ability_index, is_hidden) ON CONFLICT REPLACE,
  FOREIGN KEY (pokemon_id) REFERENCES Species(pokemon_id),
  FOREIGN KEY (ability_id) REFERENCES Ability(ability_id)
);

-- Moves Tables
CREATE TABLE IF NOT EXISTS Move (
  move_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  ptype TEXT NOT NULL,
  category TEXT NOT NULL,
  power FLOAT,
  accuracy FLOAT,
  pp INT,
  max_pp INT,
  generation_introduced INT,

  tm INT UNIQUE,
  tr INT UNIQUE,

  effect TEXT,
  zmove_effect TEXT,

  description TEXT,


  /* Targets */
  target_description TEXT
);


CREATE TABLE IF NOT EXISTS LearntByLevelUp(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  move_id INT,
  pokemon_id INT,
  level INT,
  FOREIGN KEY (move_id) REFERENCES Move(move_id),
  FOREIGN KEY (pokemon_id) REFERENCES Pokemon(pokemon_id)
);

CREATE TABLE IF NOT EXISTS LearntByTechnicalMachine (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  move_id INT,
  pokemon_id INT,
  tm INT,

  FOREIGN KEY (move_id) REFERENCES Move(move_id),
  FOREIGN KEY (pokemon_id) REFERENCES Pokemon(pokemon_id)
);

CREATE TABLE IF NOT EXISTS LearntByTechnicalRecord (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  move_id INT,
  pokemon_id INT,
  tr INT,

  FOREIGN KEY (move_id) REFERENCES Move(move_id),
  FOREIGN KEY (pokemon_id) REFERENCES Pokemon(pokemon_id)
);


CREATE TABLE IF NOT EXISTS LearntByEvolution (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pokemon_id INT,
  move_id INT,
  
  FOREIGN KEY (pokemon_id) REFERENCES Pokemon(pokemon_id)
  FOREIGN KEY (move_id) REFERENCES Move(move_id)
);

CREATE TABLE IF NOT EXISTS LearntByMoveTutor (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pokemon_id INT,
  move_id INT,
  
  FOREIGN KEY (pokemon_id) REFERENCES Pokemon(pokemon_id)
  FOREIGN KEY (move_id) REFERENCES Move(move_id)
);

CREATE TABLE IF NOT EXISTS LearntByTransfer (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pokemon_id INT,
  move_id INT,
  
  FOREIGN KEY (pokemon_id) REFERENCES Pokemon(pokemon_id)
  FOREIGN KEY (move_id) REFERENCES Move(move_id)
);

CREATE TABLE IF NOT EXISTS LearntByEggMove (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pokemon_id INT,
  move_id INT,
  
  FOREIGN KEY (pokemon_id) REFERENCES Pokemon(pokemon_id)
  FOREIGN KEY (move_id) REFERENCES Move(move_id)
);
