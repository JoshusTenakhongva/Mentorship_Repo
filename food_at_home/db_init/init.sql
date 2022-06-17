--CREATE DATABASE IF NOT EXISTS food_at_home;

\c food_at_home
DROP TABLE pantry_fact; 

DROP TABLE measurement_dim; 
DROP TABLE ingredient_dim; 
DROP TABLE recipe_dim; 

CREATE TABLE IF NOT EXISTS measurement_dim (
    measurement_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    full_name TEXT NOT NULL,
    short_hand TEXT, 
    alt_name_1 TEXT, 
    alt_name_2 TEXT, 
    alt_name_3 TEXT
);

CREATE TABLE IF NOT EXISTS ingredient_dim (
    ingredient_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    edamam_id TEXT NOT NULL, 
    ingredient_name TEXT NOT NULL, 
    link TEXT NOT NULL, 
    calories_k INT, 
    fat_g INT, 
    protein_g INT, 
    carbs_g INT, 
    expiration DATE
); 

CREATE TABLE IF NOT EXISTS recipe_dim (
    recipe_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    link TEXT NOT NULL, 
    calories_k INT,
    fat_g INT, 
    protein_g INT, 
    carbs_g INT, 
    servings INT
);

CREATE TABLE IF NOT EXISTS pantry_fact(
    id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    fk_recipe_id INT, 
    fk_ingredient_id INT NOT NULL, 
    fk_measurement_id INT, 

    ingredient_quantity FLOAT, 

    CONSTRAINT fk_recipe
        FOREIGN KEY (fk_recipe_id) 
            REFERENCES recipe_dim(recipe_id),

    CONSTRAINT fk_ingredient_id
        FOREIGN KEY (fk_ingredient_id)
            REFERENCES ingredient_dim(ingredient_id),

    CONSTRAINT fk_measurement_id
        FOREIGN KEY (fk_measurement_id) 
            REFERENCES measurement_dim(measurement_id)
); 
