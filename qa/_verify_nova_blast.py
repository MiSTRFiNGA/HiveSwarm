# Nova Shell vs large late-stage enemies.
# Expected FAIL on 0.6.1:
#   explode() hardcodes 22 and tests d < blast (center-to-center), so a Hive-Core-scale
#   colossus (r≈151) hit on the surface is OUTSIDE a 78px blast and takes 0.
import os, sys
from playwright.sync_api import sync_playwright

PORT = sys.argv[1] if len(sys.argv) > 1 else "8795"
fails = []


def check(label, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + label + ("  " + detail if detail else ""))
    if not cond:
        fails.append(label)


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    p = b.new_context(service_workers="block", viewport={"width": 400, "height": 860}).new_page()
    p.goto(f"http://127.0.0.1:{PORT}/index.html?nocache=nova", wait_until="load", timeout=20000)
    p.wait_for_timeout(400)
    p.keyboard.press("Enter")
    p.wait_for_timeout(300)

    r = p.evaluate("""()=>{
      enemies.length=0;
      const big={x:0,y:0,r:151,hp:2400,maxHp:2400,type:{id:'enemy.colossus',name:'Colossus'},
                 hit:0,isBoss:true,speed:30};
      const small={x:200,y:0,r:16,hp:100,maxHp:100,type:{id:'enemy.shambler',name:'Shambler'},
                   hit:0,speed:60};
      enemies.push(big, small);
      explode(151, 0, '#ffe066', 78, false, 0,
              {damage:30,shards:0,color:'#ffe066',blast:78});
      return {
        bigDealt: 2400-big.hp,
        smallDealt: 100-small.hp,
        novaForge: (EDIT.weapons.find(w=>w.id==='weapon.nova')||{}).damage
      };
    }""")
    print("  result:", r)
    check("surface hit on r=151 enemy deals FORGE damage (~30)",
          r["bigDealt"] >= 25, f"dealt {r['bigDealt']}")
    check("blast does not use leftover hardcoded 22 on a surface hit",
          abs(r["bigDealt"] - 22) > 2, f"dealt {r['bigDealt']}")
    check("distant small enemy is not fully deleted by the same blast",
          r["smallDealt"] < 50, f"dealt {r['smallDealt']}")

    sync = p.evaluate("""()=>{
      const n=EDIT.weapons.find(w=>w.id==='weapon.nova');
      n.damage=30;
      persistForge();
      if(typeof applyForge==='function')applyForge();
      const held=(heldWeapons.find(w=>w.id==='weapon.nova'))||null;
      const src=EDIT.weapons.find(w=>w.id==='weapon.nova');
      return {forge:src.damage, held:held&&held.damage, hasHeld:!!held};
    }""")
    print("  forge sync:", sync)
    check("FORGE nova damage sticks at 30", sync["forge"] == 30, f"got {sync['forge']}")
    b.close()

print()
if fails:
    print("FAILED:", "; ".join(fails))
    sys.exit(1)
print("ALL CHECKS PASSED")
