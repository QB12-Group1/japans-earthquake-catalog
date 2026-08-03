UPDATE earthquakes SET place = trim(place) WHERE place IS NOT NULL;
