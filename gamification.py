def initialize():
    global cur_hedons, cur_health

    global cur_time
    global last_activity, last_activity_duration
    global tired
    global elapsed_time

    global last_finished
    global bored_with_stars

    global last_star1, last_star2, cur_star_activity, last_star3

    global last_run, last_textbooks, run_total_duration
    global x

    # set up the starting values
    cur_hedons = 0              # how much "fun" we currently have
    cur_health = 0              # how much "health" we currently have
    last_star1 = 0              # counts how many times a star was offered
    last_star2 = 0              # tracks time since star appeared
    last_star3 = 0              # another counter for star timing

    cur_star = None             # store the current star activity (not used anywhere)
    cur_star_activity = None    # activity that has an active star bonus

    bored_with_stars = False    # once too many stars, we get bored of them

    tired = None                # whether player is tired

    last_activity = None        # last activity done
    last_activity_duration = 0  # duration of last activity
    elapsed_time = 120          # elapsed time since last rest
    cur_time = 0                # overall time tracker

    run_total_duration = 0      # running total used for health bonus

    last_finished = -1000       # last finished time marker
    x = 0                       # unused counter but kept for consistency


def star_can_be_taken(activity):
    # star only works if the offered activity matches and we aren’t bored
    if activity == cur_star_activity and not bored_with_stars:
        return True
    else:
        return False


def perform_activity(activity, duration):
    global cur_star_activity, last_star1, last_star2, bored_with_stars, x
    global elapsed_time, tired, last_star3
    global run_total_duration, cur_hedons, cur_health

    # if too many stars, we get bored
    if last_star1 > 2:
        bored_with_stars = True

    # check if tired (less than 120 minutes since last full rest → tired)
    if elapsed_time < 120:
        tired = True
    else:
        tired = False

    # running activity health calculation
    run_under_duration = run_total_duration
    if activity == "running":
        run_total_duration += duration
        if run_total_duration <= 180:           # healthy running time up to 180
            cur_health += (duration * 3)
        elif run_total_duration > 180:          # after 180, health gain slows
            if run_total_duration - duration >= 180:  # already past 180 before
                cur_health += duration
            else:  # just crossed 180 boundary
                cur_health += (180 - run_under_duration) * 3 + (run_total_duration - 180) * 1

    # textbooks give health but reset running streak
    if activity == "textbooks":
        cur_health += (duration * 2)
        run_total_duration = 0

    # resting resets running streak
    if activity == "resting":
        run_total_duration = 0

    # calculate hedons (fun points)
    if activity == "running":
        if tired:
            cur_hedons -= duration * 2   # running while tired sucks
        else:
            if cur_star_activity == "running" and not bored_with_stars:
                # running with star
                if duration <= 10:
                    cur_hedons += duration * 3
                else:
                    cur_hedons += 30
            else:
                # normal running
                if duration <= 10:
                    cur_hedons += duration * 2
                else:
                    cur_hedons += 40 - (duration * 2)

    if activity == "textbooks":
        if tired:
            cur_hedons -= duration * 2   # studying while tired = boring
        else:
            if cur_star_activity == "textbooks" and not bored_with_stars:
                if duration <= 10:
                    cur_hedons += duration * 3
                else:
                    cur_hedons += 30
            else:
                if duration <= 20:
                    cur_hedons += duration
                else:
                    cur_hedons += 40 - duration

    # update elapsed time
    if not tired:
        elapsed_time = 0
    elapsed_time += duration

    # star timers update
    if cur_star_activity is not None:
        if last_star3 != 0:
            last_star2 += duration
        last_star3 += duration
        if last_star3 >= 120:
            # reset counters after 2 hours
            last_star3 = last_star2
            last_star2 = 0
            last_star1 = 0

    # star disappears after activity
    cur_star_activity = None


def get_cur_hedons():
    return cur_hedons


def get_cur_health():
    return cur_health


def offer_star(activity):
    global cur_star_activity, last_star1, bored_with_stars, last_star3
    last_star1 += 1
    if last_star1 > 2:
        bored_with_stars = True
    else:
        cur_star_activity = activity  # star can apply to any offered activity


def most_fun_activity_minute():
    # if tired and no star, best is resting
    if tired and cur_star_activity is None:
        return "resting"
    elif tired and cur_star_activity == "textbooks":
        return "textbooks"
    elif tired and cur_star_activity == "running":
        return "running"
    elif cur_star_activity == "textbooks":
        return "textbooks"
    elif cur_star_activity == "running":
        return "running"
    else:
        return "running"   # default choice


if __name__ == '__main__':
    initialize()

    # Test 1
    perform_activity("running", 10)
    print("Test 1: Running 10 min (not tired)")
    print("Expected Health: 30, Actual:", get_cur_health())
    print("Expected Hedons: 20, Actual:", get_cur_hedons())
    print()

    # Test 2
    initialize()
    perform_activity("running", 200)
    print("Test 2: Running 200 min straight")
    print("Expected Health: 560")
    print("Actual:", get_cur_health())
    print("Expected Hedons: -360, Actual:", get_cur_hedons())
    print()

    # Test 3
    initialize()
    elapsed_time = 100   # force state to tired
    perform_activity("textbooks", 10)
    print("Test 3: Textbooks while tired for 10 min")
    print("Expected Health: 20 (10*2), Actual:", get_cur_health())
    print("Expected Hedons: -20 (10*-2), Actual:", get_cur_hedons())
    print()

    # Test 4
    initialize()
    offer_star("running")
    perform_activity("running", 5)
    print("Test 4: Running 5 min with star")
    print("Expected Health: 15 (5*3), Actual:", get_cur_health())
    print("Expected Hedons: 15 (5*3 with star), Actual:", get_cur_hedons())
    print()

    # Test 5
    initialize()
    offer_star("running")
    offer_star("running")
    offer_star("running")  # now bored
    print("Test 5: Offering 3 stars in a row")
    print("Expected: star cannot be taken anymore → False")
    print("Actual:", star_can_be_taken("running"))
    print()

    # Test 6
    initialize()
    offer_star("textbooks")
    print("Test 6: Most fun activity with textbooks star")
    print("Expected: textbooks")
    print("Actual:", most_fun_activity_minute())
    print()

    # Test 7
    initialize()
    perform_activity("running", 100)
    perform_activity("textbooks", 20)
    print("Test 8: Run 100 then study 20")
    print("Expected Health: 300 (running) + 40 (study) = 340")
    print("Actual:", get_cur_health())
    print()

    # Test 8
    initialize()
    elapsed_time = 100  # force into tired zone
    perform_activity("running", 10)
    print("Test 9: Running while tired")
    print("Expected Hedons: -20 (10*-2)")
    print("Actual:", get_cur_hedons())
    print()

    # Test 9
    initialize()
    offer_star("running")
    perform_activity("running", 130)  # push past 120
    print("Test 10: Running 130 with star, star should expire after 120")
    print("Expected: star no longer valid → bored_with_stars or reset counters")
    print("Actual bored_with_stars:", bored_with_stars, "last_star1:", last_star1)

