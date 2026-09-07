export function isValidWalk(walk) {
    if (walk.length !== 10) return false;
    let norths = 0, easts = 0;
    for (const step of walk) {
        switch (step) {
            case 'n':
                norths += 1;
                break;
            case 's':
                norths -= 1;
                break;
            case 'e':
                easts += 1;
                break;
            case 'w':
                easts -= 1;
                break;
        }
    }
    return norths === 0 && easts === 0;
}
