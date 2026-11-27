#!/usr/bin/env python3
"""make.fun news-image-20261126 entry.

Draws a one-page newspaper front page summing up the world news of
Thursday 26 November 2026 and writes it as entry.png into the directory
named by MAKEFUN_OUTPUT_DIR (or /output when that variable is absent).
Standard library only. No network, no file reads at run time: all glyph
shapes are embedded below as compact encoded outline data, extracted
from the DejaVu fonts on the build machine (see GLYPH NOTE at the end).
Deterministic: no clock, no randomness, fixed iteration order.
"""
import binascii
import math
import os
import struct
import zlib

W = 1024
H = 1024

CREAM = (250, 243, 224)
WHITE = (255, 255, 255)
CARD = (253, 250, 242)
NAVY = (13, 27, 62)
NAVY_LT = (38, 58, 105)
RED = (196, 30, 30)
RED_DK = (150, 20, 20)
GREY = (92, 92, 88)
LINE = (180, 172, 150)
LAND = (196, 210, 218)
LAND_LN = (120, 140, 158)
GOLD = (176, 124, 18)
TEAL = (0, 110, 110)
ORANGE = (198, 104, 0)
PURPLE = (90, 60, 140)
GREEN = (0, 128, 68)
BLUE = (30, 90, 180)
OCHRE = (146, 98, 18)
MAGENTA = (168, 40, 108)
SLATE = (88, 88, 96)

CHARSET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,;:!?-\'"()[]%$&@#*+/=<>—–’“”•×…'
SERIFB = "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"
SANS = "8VCD+KoUpEzL0IAIjG2O0DA8IpXnDAjCgGxKAjC/FpDA+VDTqGkLAvIiFAmBCgBGcKWOSUMYIcCgBBgBHcLYRUVObKfGlBCThF0JAhH2EAiBCeGYIWMQQKUIWCcBaHWJUPQVMXIdGhBCjB7HyCiIA2BBwBJqBNiBVcZUfMjBEpBDfDdLXLXRRVNZJdHkBJgBNaTWVSbOdIfClBDtBNpBTjBddlBXrBPzBJ7BDrIAsWBzB0UwVApD1BqB3Be5BS/BE7BDzBNtBZlBhBdpBVzBL9BDlCEjCM9BWzBerBmBhBuBX0BN8BFgCG6BS4Be2BqBApD3Bf3BV9BN/BDvCGnCU9BgBzBuBrB4BdiCRsCF0CG2CSsCeiCsB4B0BuB+BgBoCUwCGiCD8BN6BV2Bf0YCTqG4UAjS6DAoCE+BMyBWqBegBqBWyBO8BEmCDmCN8BVyBfoBpBexBW9BOnCET/GyCwGAmDF2CPoCb6BnBsBzBgB/BUrCG5CF5CTtCf/BrBzB5BnBnCb3CPjDFvGAoUBMkDqX4OAAzCxLAA9GiLAAzChLAAvI8LAAzChPAsSBKkDqXuNAAzCnKAA7GoJAA1CnJAAjLlDA6YB3BiTqDAqGlFAAyCqIAA/J9BjBjCbnCPtCDxCGpCU/BgB1BsBpB4BfiCRsCF2CG2CSuCgBiCqB4B2BsBgCgBqCUyCGoCDiCNgCV6BfApD5BqB7BchCUjCE/BD3BNtBXnBhBdpBTzBN9BDnCElCO9BUzBerBoBfuBX4BNgCF0BCsBIoBMkBQiYBMkDqXmDAAxJuLAAyJmDAApXlDAAkLtLAAjLlDAuJBEkDqXmDAApXlDAuJBWkDqXmDAA1VD9BJ1BPrBVjBdZjBTtBLzBBlBAA0CeAgBCaIUMQQOWIeEmBCsBgVBLkDqXmDAA5JuK6JiEAxL7KsMtMjEAlLoLAnLlDA6RBGkDqXmDAA1UqLAAzCvOA0bBNkDqX4EA+F7P+F8P4EAApXjDAAwU/F/PjDAhGgQAvUhDA+XBKkDqXoEAsKvTAwTiDAApXnEArKwTAvThDAmZChB0MmVzBFvBNnBZjBjBbrBTzBL7BDjCEhCM7BUzBcrBkBjBoBZwBP0BD0BEuBQoBakBkBcsBU0BM8BEiCDkCL8BT0BbsBjBkBnBatBOzBGhBAyCqCFiCT8BhByBtBqB3BchCSrCGzCFzCRpCbhCpB5BxBtB7BfhCTpCFrCGhCU7BgBxBuBpB6BbiCRqCF0CG0CSsCciCqB4ByBuB8BiBiCUsCGqTCTqG4UA3I+DAiBCeGYMWQQUMYIcCgBBgBHaLYPWVOXMdIhBCVjHyCkHA8BDyBJsBRkBXcfUlBMtBExBDzBLtBTlBbfjBXrBRxBJ7BD9DAArJlDAmZChB0MmVzBFvBNnBZjBjBbrBTzBL7BDjCEhCM7BUzBcrBkBjBoBZwBP0BD0BEuBQoBakBkBcsBU0BM8BEiCDkCL8BT0BbsBjBkBnBatBOzBGmBsE3UmExE5DAtD4DZBPArCGhCU7BgBxBuBpB6BbiCRqCF0CG0CSsCciCqB4ByBuB8BiBiCUsCGqCFiCT8BhByBtBqB3BchCSrCGzCB9BJ5BP1BXvBbrBjBjBnBfvBXoWCjBmO+KgBRgBberBgB3BmDrGrDA/CgGRiBRcRWRQnBS1BGtDAA7JlDAAqXkHA8BB0BJsBRkBXcdSjBMrBExBBhBFdJbNZRTVRZPdJT7H6JApI+DAiBCeGaMUOSUKWIaCgBBeHaJYRSTOZMdGhBCqUBxCkRyWAhD3BYzBQxBKxBElBBhBFdJXNTRNTHZDZIrBWfSLaJgBJmBH8BL2BNsBPmBVgBXWdShBKlBCrBDxBNtBVlBfdnBZxBP3BLhCB3BC5BK7BO/BUAoD+Bd8BV6BL6BDoBCkBGeKaQWSOWIaEeBaFYLUNQTQXMfKhBK9BM1BMrBQjBUdWVaPeJkBBqBEuBMqBWkBgBgBmBYsBS0BK6BEqDJwDbyTBIDqX4TAAzCnIAA1UlDAA2UpIAuXBmB4CqXmDAAlOE1BIvBMnBUdaVgBRmBJuBBsBCmBKgBSaWSeOoBIwBE2BAmOkDAAxODjCN7BVxBfpBnBfxBX3BNhCDjCE5BOvBYnBgBfqBVyBN8BFkC8VBHkJA7IqXqDAsHzTuH0ToDA7IpX0fBNiBqXmDA8E1T+E2TyDA8E1T8E2ToDA7FpX/DA7EoU/EnU/DA+VBMgCqXsDA6F1I6F2IuDAvHlLgIjMtDAvG+JzG9JtDAqIuMyTBJBqXsDAwGxJuGyJsDAnIlMAjLlDAAkL+VBK6BqXqSAArC3OpSkPAAzChTAAsC4OqSrOA0TCWgL6IzBBrBDhBHZLRPNRHXBdIpBYhBmBVyBHkBEgBKeSYWUeOiBKmBCqBAWzB8CmBA/J7CAA0ChBrBrBdzBR/BFnBCjBKfObWVaPeJiBBoBEsBMmBUgBackBUsBQyBI8BEgEAAIBeHaLYTSVQbKdIjBCvBDtBHrBNrBTA0CyBSwBMwBIsBC6BDyBLoBTiBbajBUpBKzBE7BqUChByP4IBwBHqBLmBTeVaZSfKhBEhBDfJZRVZTdLlBHpBBvBCvBIrBMjBUfWZaRgBJiBDiBEgBKaSWaUgBMkBIsBCwBd3JkGgBqBoBgByBS4BGyBFqBNoBZiBjBcrBUxBM3BE9BD/BL3BTxBbrBhBhBnBZpBPxBD3BGxBSnBefsBAzC9CAAqY+CA0RBwB0P6QA1CnBUlBMnBInBEpBDlBJfRZZVdPlBJpBBvBCvBKrBQjBWfaXgBRmBJqBDoBCoBImBOoBSAzCvCbpBFtBB7BE1BQtBYnBiBhBsBVyBN6BFgCGgCO6BWyBiBsBoBiBwBY4BO+BGyCJwCZqUCewO8OAuJ8CAApY7CAA0CfrBnBdvBR5BFvBErBQnBahBiBbsBTyBL4BDgCE+BM4BUyBcsBiBkBoBasBOwBG6BFwBRoBfgBpBhB3JjGCvBIrBMjBUfWZaRgBJiBDiBEgBKaSYaSgBMkBIsBCwBBwBHqBLmBReXaZSfKhBEhBDfJZRVZTdLlBHpBBvB2TCsBgSwJAtBnNAGrBMnBQhBYZcViBPmBJqBB0BC0BKwBQyBYA3CxBRzBNzBHzBB/BE5BOvBarBiBhBqBXyBN4BF+BGiCO6BWyBgBsBqBkBuBa2BO8BG0BFwBLqBXkBfclBWvBMzBE5BR7CaDkBHgBLcRYXUXOdIfEjBDhBHbLZTTXPbJhBFjBoLBa8LqYArC3CApBFZNPbDrBAxB4EAAnC3EAAnP7CAAoP3CAAoC4CAAoBCqBImBOeUaYSgBOkBIsBCqUChBwO+IBwBHqBLkBReVYbQdMjBChBBfLZPXXRdLjBHpBBvBCtBIpBMjBSdYXaRgBJiBDkBEeKcSWYSeMkBIqBCuBzB8C3GBjCL5BTvBbnBjBdrBV1BL7BD7CGzCWA6CoBToBLoBHoBBqBCmBIeQaUUaOiBImBCsBAuBfpBnBfvBR5BFxBErBQlBYhBiBbqBTyBL2BD+BE+BM4BUwBcsBiBiBmBYsBOyBG6BFwBToBdgBpBA0C8CAoUBlByRyKAxK7CAAwKBkBFgBJcLWRSVMXIdCjBDdHbPXTRZNdHhBBnBA7J9CAAqY+CAAxJkBuBqBewBU2BGuBDoBLgBRcZWhBQnBIvBE1B8ICEgDwR8CAAvR7CAEAqY8CAAzD7CA8ICWgDwR8CAA5RBxBHpBLjBRZXVdNjBJpBBhBAAsCYAYCUGQGMMIOGWEeAiBEA0Y8CAAzD7CAwSBL8CqY+CAArOyIyH2DApJlI2JpJ3DA7IyIAxI9CA8IBEgDqY8CAApY7CAmfBgC0QkOmB2BuBmB0BW8BIqBDkBLeRcbUhBOnBKtBC1BAxK7CAAwKBkBFiBHaLWPSTMXIbChBDdHZPVTRZNdHhBBnBA7J7CAAwKBkBFiBHaLWRSTMXIZChBDdHZPVTTZLdHhBBnBA7J9CAAwR+CAA3CiBuBoBeyBU4BG4BHwBXkBlBazBoUBlByRyKAxK7CAAwKBkBFgBJcLWRSVMXIdCjBDdHbPXTRZNdHhBBnBA7J9CAAwR+CAA3CkBuBqBewBU2BGuBDoBLgBRcZWhBQnBIvBE1ByTChB6JwPjBDdJbRXZRfNjBHpBBvBCvBIpBOlBSdYZaRgBJkBDiBEgBKaSYaSgBOkBIqBCwBBuBHqBNmBRgBXYZSfMhBEhBAuC4BFyBNsBXmBhBerBWxBM5BE/BDhCL5BVxBdpBlBhBrBXxBP3BD5BExBQrBYlBiBdqBTyBN6BDiCEgCO6BUyBesBmBiBsBYyBO6BGqUCe6F0CAnJ9CAAkY+CAAzCgBqBoBgByBS4BGyBFqBNoBZiBjBcrBUxBM3BE9BD/BL3BTxBbrBhBhBnBZpBPxBD3BGxBSnBefsBhB4JkGBwBHqBLmBTeVaZSfKhBEhBDfJZRVZTdLlBHpBBvBCvBIrBMjBUfWZaRgBJiBDiBEgBKaSWaUgBMkBIsBCwBqUChB4E4ICvBIrBMjBUfWZaRgBJiBDiBEgBKaSYaSgBMkBIsBCwBBwBHqBLmBReXaZSfKhBEhBDfJZRVZTdLlBHpBBvBd4JjGfrBnBdvBR5BFvBErBQnBahBiBbsBTyBL4BDgCE+BM4BUyBcsBiBkBoBasBOwBG6BFwBRoBfgBpBA0C8CAAjY7CAkNBWkN6OfOnBElBDfJbPVVTbLhBHlBBrBAnJ9CAAwR+CAA3CgBuBqBe0BU+BGWBYD2QBrCmOgRA3CnBSpBMpBIrBCfAbDXHTHNLJNHRBTGbSVQHWJcHiBHgBHsBLmBLgBPYRSVOXGdEfDjBLhBTbZXhBTnBPrBHzBB9CIxBMzBOAgDyBXyBPyBJwBD6BGqBQacIkBFgBRYPKXKfKnBKfIlBKhBMbOVSRULYFcBeEmBKgBScYYeUmBMqBIwBEgDHsBJoBLyMBe8FwWA/E8FAAnC7FAAvJAdEZGRINMHQFWDaB+CAArC9CAvBCpBIfMXSRYLgBHoBBwBAwJjCAAoCkCAAgFoUClB4C8GA0K8CAAvKAjBGhBKZOVSRULaHeBiBCgBKcOWUUaOgBIiBCmBA+J8CAAvR7CAA2CjBrBpBfvBR1BFtBEnBKhBUbaTgBPqBJuBB2BBmHiL+SBHewRiDAwF1OuF2OiDAxGvR9DAmaBNsBwR8CAyDzNyD0NsDA0DzNyD0N8CAxEvRrDA3DsO5DrOrDA+SBMyRwRpGvI0G/IrDAjF8GhF7GrDA6GkJnGsIsDA0EnG2EoG+SBWqKzBTtBRjBTbRTrBX3BFpCAAsC4BAgBEaOKMMSMYMgBQoBhHoRiDAwF1NuF2NiDA6QBK4BwR2NAAzC5KxM6KAApChOAA0C6KyMtKAsUChBmKoVlBDdPbXVfPrBNzBF/BDnCEnCG9BOzBQrBWhBcXeNmBDkBEgBOcYWiBQsBM0BI+BCoCBoCHgCL0BPsBVgBbYfQjBEhBAwC6BF0BRsBfmBrBc1BUhCOtCE5CD3CNtCThCb3BlBpBrBfzBR5BF7BGzBSrBgBjBqBd4BTiCLuCD4CE6CMuCUiCe2BkBsBsBgB0BS8BGsUBLgE0CkFAA6RzFjBA8C0FkBkDAA1UkFAAzCrNAsUB2BkG0CgLAAzC3OAA0CeiBkBkBqBsBwBuBsBuBkBmBccQSqByBaqBOmBGkBDcFaNYRUVQZMdGfEvBFzBL1BT5BdAmD8BW2BQyBIwBE2BDyBJqBRmBZefWjBMnBEtBDtBLpBXtBnBzBHJRRVXdflBlBrBrBxBzB5B7BsUBxCgNyMiBJeNaRWVSZObGfEjBFzBNrBXnBfhBpBZxBT5BJhCDhDIlDcAiDsBVwBN0BJ0BDuBCmBIiBMcQWUOaKeCgBBgBHcPYTUXQdMjBIlBC1CAAyC6CAkBCeGaKWMSQMUIYCaDcFWNWRQVOZKfGjBCpBDvBFvBL3BPA6C4BO0BKgDI2BDwBJqBPkBVebWhBMlBEpBBdFZLZPVpBjB5BXsUCDkMyU/HtMgIALbmPgEAAlPqDAAzCpDAAvFjDAAwFxKAAiDsUBxBuDqXuMAAzCvJAA3FsBMsBE6BD2BNuBVmBdgBjBYrBOxBE1BD5BNxBXrBfjBpBbxBV3BL/BD/CIjDYAmDsBVwBPyBH0BDoBEmBIgBOaUWYQeKgBCmBBkBJiBPcVaZSfQlBInBCxCHnBLpBPsUChByK+MfDbHZNVTRZLdHhBBlBClBIhBMdSZWTaNcJgBBgBCcKaOWUSaMeIiBCmBBmBHiBLeRaVUZObIfEyBoG8JA7CrCctCKtBFpBLhBTddXlBRvBL1BF/BiBmBoBcuBS0BG2BDuBNqBTkBdclBUrBMvBG3BF3BLvBVrBbjBlBfpBVvBL1BD7BG1BStBgBlBqBd4BViCLuCD4CE0CQsCaiCmB4BuBuB0BiB8BUiCGuCHwCVsUBH0CqXgPAApBvI/VnDA+H2UlLAsUDhBmKiLhBBdHbLVPRVLXHbBfCfIbMXSVWPcLeHiBBiBCeIaMYQSWMYIcCgBBgBHcLYRWXQZMdIhBChClDsBdKbMVSTUPYLaFcBeCqBMmBUiBcckBWoBSuBI2BE0BDuBHqBRiBVcbUhBMlBEpBBdHbJZPXTTXRZLdJiBLeNaRWVSbObGfEhBDzBNrBTlBbflBZrBRxBJ5BD5BEzBKrBSjBadgBTmBLsBD0BCiBIgBMcScWWcSeOiBMhBjB+ECZGXMVQRUNYJaFgBBeCcGYKUOQSKWIYCaBcHYJWPSTOXKbGdCfBZFXJTNPRLVFXBbsUCyBwDQA8CuCbsCJwBEoBOkBUceYmBSuBM4BIgChBlBnBbvBRxBF1BGvBMnBWjBcbmBVqBLyBD4BE2BOyBUqBemBmBeqBWwBO2BE8BF2BRuBfmBrBe1BUhCOtCE5CFzCPpCZhCjB5BtBtBzBf7BTjCFrCGxCYhBqG8JgBCcKaOWUQaOeGiBCmBBmBFiBNePaVUZObKfCfBdJXNVTRZLdHhBBlBClBIhBMdSZWTYNeJgBBmKAmKBEuDgEqDAA/DpDAmKBG4DgEqDAA3CxC/E/BAoBgF4KCE4DyQqDAA/DpDAGAxIqDAA3CxC/E/BAoBgF4KCE4DgEqDAA/DpDAEAyQqDAA/DpDA6MCE6EgEmDAA/DlDAGAqXmDAAlKJzFxCAJ0FgRCEkGgEkDAA/DjDAsBiDoG/CAAuCEuBKkBWkBmBoBsBsBaaQYKYCYHoBXgBlBWvBGpBDrBNrBTvBdA+CuBYwBSyBKyBEsBDoBHiBPeTYZSdKhBElBDlBNhBXlBlBnBrBpBVVLPNZDXBRAXyLBEyBiKuIAAxCtIA6IBE4FqXA1I1CAA2I4OCE4FqXA1I1CAA2IEyIAA1IzCAA2IwMBS+JoY5BxDpBvDXxDHxDIzDYxDqBvD6BzDvCAhC2DtByDbyDJwDKwDawDwByDiC0DwMBTyCoYwCAiCzDuBxDcvDKvDJvDbxDtBxDhC1DvCA6B0DqBwDYyDI0DHyDXyDpBwD5ByDwMBI4CqY0GAAnC3DAAhY4DAAnCzGAwMBI4JqYAxczGAAoC4DAAiY3DAAoCseFZoXoKTBRFPLNPRrBF7BG5BSrBOPQLSFUDUESGQMOQSsBG6BF6BRuBNQPMRGTChBAgCmBDiBJcPaZUbOjBKnBCrBBrBJnBNhBTdZXbPhBLlBBlBChBMbQZYTeNiBJoBBsBCuBKmBOkBUeaYeQgBKmBEZjQwJTBRFPLNPRrBF7BG5BSrBOPQLSFUDWESGQMMQUsBG6BF6BTuBNQNMTGTCEkOgCwCAzOlYvCAhBQmYmBDiBJcPaXWdOjBIlBEtBDrBHnBNhBVdXXdPhBLlBBlBCfMdQZYTeNiBHoBDsBEuBImBOkBWcYaeQiBKkBEsUD2B6K1ExBAA2EzBE1BIzBO1BUA6C0Bb0BT2BL2BDAkHzBKrBOjBQbUVYPcJeDkBEmBKiBSeYaeWkBQqBKwBGA2DyBAAzD6CJ0CTA3CzCgB5COA1G2BJsBNmBReTYZSbKfClBDnBJjBRdXZfVlBRrBJxBHKxBgMAuGzBLjBVXdHnBIlBWbkBV2BNKyB/CA3G4BOoBWYgBIoBHoBVgBnBW5BO+YCR4HyMlBnBbpBPnBFrBEhBKfQdYXcVgBPiBHoBDsBEsBMoBUmBc5BhGoK+HjIauBUwBM2BI2B8CALhCT/Bf/BnB/BsEtE/DAlCqC1BnB3BZ5BR/BD5BEzBMtBWpBefmBXoBNwBFyBI+Ba6BqB4B6ByBTgBPgBJeBeCoBMiBQeYagBWiBQmBIsBE0CH0CbA7CrBWnBOlBKjBCvBFjBTZfHnBEZMZWdmBpBggBChB8LsIEhBGdKZQVURWLaHeBeCYIYMSSQWMaGeCiBBiBHeJaPWTSVMZIdCbBZHVLTRNVLZFdDhBtDyIzEfhBlBXpBNvBDnBElBMfUdaViBRmBJqBDwBEwBKsBSmBYiBcagBUmBMoBEwBFqBNmBVgBhBAiCmCAAvLkBIeOaUYYSeMiBImBCqBD0BLyBTsBbqB3B6BlCqBtCazCI7BD5BL1BTzBbjBZffdjBXnBTpBLrBJtBBtBItCUnCkB/BwB5B4BtBiChBmCTuCF+BEgCS8Ba2BkBsB3B/BpBnCfpCTpCF5CI1CYrCoBlC4B3BkCpBsCX2CH8CI4Ca0CoBuC4BkCmC4BwCqB2CY8CI0BByBHwBNwBRqBXoBdkBfiBlBgBzBY1BQ7BE7BD9BP3BXvBjBpBpBfzBX5BPhCF6aCEsQiOxEApBlFyEAchBkOzBvGyEA2BwGwCAzBvG8EAAtCvFAnBlF+EAArCxFAzBvGvCA0BwGzEAzBvGvCA0BwG7EAAsCwFAoBmF/EAAuC0FA0BwGgQBSiPwTzFhD0FhDdvBnFmDA9F3BAA+FnFlDdwB0FiDzFiDewBoFjDA8F4BAA7FoFkD6aBM4OiUA1I2IAA1C1IAA1IzCAA2I3IAA2C4IAA2I4KBEkIqX0CAjIpazCA6aCEsDwOiUAAzChUAEA3DiUAAzChUA6aBHuX4PjQ3FkQ1FA5ChUoHAyCiUqH6aBHsD4PA8CiUpHAxChUnHA6CkQ2FggBBEyB8J8cAAnC7cAgQBEyB8J8MAAnC7MAmKBGiEqXqDAArCxC9EhCAqB+EyQCGgG0PnDAA4CwC+EiCApB9EGuG3CpDAA4CyC+EgCAnB9EyQCGgEqXqDAA1CxC/E/BAoBgFGsG2CqDAA1CxC/E/BAoBgF8SBhB6E8LCeIcOaSWYSYOcIgBCcBcHaNWRSVOZIbCdBdHZNZRVXTXLbHdDdEbIXMXURWNaHaBe6aBMuWmRjHlHkHjH7B7BlHkHjHjH7B8BkHkHjHmH8B8BkHlHmHmHggBDEsOgEoDAA/DnDAE0KgEqDAA/DpDAEpVgEqDAA/DpDA"


_ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_IDX = {c: i for i, c in enumerate(_ALPH)}


def _dec_u(s, i):
    n = 0
    sh = 0
    while True:
        v = _IDX[s[i]]
        i += 1
        if v >= 32:
            n |= (v - 32) << sh
            sh += 5
        else:
            n |= v << sh
            break
    return n, i


def _dec_s(s, i):
    n, i = _dec_u(s, i)
    return (n >> 1) ^ -(n & 1), i


def _decode_font(data):
    """Decode one packed font string into {char: (advance, contours)}.
    Contours are lists of (x, y) integer points in a 512-units-per-em
    grid, y pointing up, baseline at y = 0."""
    glyphs = {}
    i = 0
    for ch in CHARSET:
        adv, i = _dec_s(data, i)
        ncon, i = _dec_u(data, i)
        contours = []
        px, py = 0, 0
        for _ in range(ncon):
            npts, i = _dec_u(data, i)
            contour = []
            for _ in range(npts):
                dx, i = _dec_s(data, i)
                dy, i = _dec_s(data, i)
                px += dx
                py += dy
                contour.append((px, py))
            contours.append(contour)
        glyphs[ch] = (adv, contours)
    return glyphs


SERIFB_FONT = None
SANS_FONT = None
_RASTER_CACHE = {}


def _glyph(font, ch):
    return font.get(ch) or font["?"]


def _glyph_adv(font, ch):
    g = _glyph(font, ch)
    return g[0]


def _spans(polys, y0, y1):
    """Nonzero-winding scanline spans for a list of polygons (float
    coords). Overlapping same-direction polygons union (so a bold
    glyph drawn twice, offset, fills solid), while counter-wound
    inner contours stay holes. Yields (row, x_start, x_end) with
    x_end exclusive, for integer rows in [y0, y1)."""
    for r in range(y0, y1):
        yc = r + 0.5
        ev = []
        for poly in polys:
            n = len(poly)
            for k in range(n):
                x1, y1 = poly[k]
                x2, y2 = poly[(k + 1) % n]
                if y1 == y2:
                    continue
                if (y1 <= yc < y2) or (y2 <= yc < y1):
                    x = x1 + (yc - y1) * (x2 - x1) / (y2 - y1)
                    ev.append((x, 1 if y2 > y1 else -1))
        ev.sort(key=lambda t: t[0])
        winding = 0
        start = None
        i = 0
        while i < len(ev):
            x = ev[i][0]
            delta = 0
            while i < len(ev) and ev[i][0] == x:
                delta += ev[i][1]
                i += 1
            prev = winding
            winding += delta
            if prev == 0 and winding != 0:
                start = x
            elif prev != 0 and winding == 0 and start is not None:
                a = math.ceil(start - 0.5)
                b = math.ceil(x - 0.5)
                if b > a:
                    yield (r, a, b)
                start = None


def rasterize(font, ch, size, shear=0.0, bold=False):
    """Rasterize one glyph to a list of runs, with 3x supersampling so
    sub-pixel stems and thin bars at small sizes still show.
    Returns (width, height, x_off, y_off, runs, advance_px) where runs
    are (dy, x0, x1) relative to the bitmap origin, x_off is the left
    edge relative to the pen position and y_off the top edge relative
    to the baseline."""
    key = (font is SERIFB_FONT, ch, size, shear, bold)
    hit = _RASTER_CACHE.get(key)
    if hit is not None:
        return hit
    adv, contours = _glyph(font, ch)
    ss = 3
    s = size * ss / 512.0
    polys = []
    for contour in contours:
        polys.append([(x * s + y * s * shear, -y * s) for (x, y) in contour])
    if bold:
        off = max(0.6, size * 0.035) * ss
        for contour in contours:
            polys.append([(x * s + off + y * s * shear, -y * s)
                          for (x, y) in contour])
    if not polys:
        res = (0, 0, 0, 0, (), adv * size / 512.0)
        _RASTER_CACHE[key] = res
        return res
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    # Output-pixel bbox, aligned to the supersample grid.
    ox0 = math.floor(min(xs) / ss)
    ox1 = math.ceil(max(xs) / ss)
    oy0 = math.floor(min(ys) / ss)
    oy1 = math.ceil(max(ys) / ss)
    w3 = (ox1 - ox0) * ss
    h3 = (oy1 - oy0) * ss
    sub = bytearray(w3 * h3)
    xbase = ox0 * ss
    ybase = oy0 * ss
    for (r, a, b) in _spans(polys, ybase, ybase + h3):
        a = max(xbase, a)
        b = min(xbase + w3, b)
        if b > a:
            o = (r - ybase) * w3 + (a - xbase)
            sub[o:o + (b - a)] = b"\x01" * (b - a)
    # Downsample: an output pixel is on when at least 2 of its 9
    # sub-pixels are covered.
    runs = []
    for oy in range(oy1 - oy0):
        row_runs = []
        start = None
        for ox in range(ox1 - ox0):
            cov = 0
            for dy in range(ss):
                o = (oy * ss + dy) * w3 + ox * ss
                cov += sub[o] + sub[o + 1] + sub[o + 2]
            if cov >= 2:
                if start is None:
                    start = ox
            else:
                if start is not None:
                    row_runs.append((oy, start, ox))
                    start = None
        if start is not None:
            row_runs.append((oy, start, ox1 - ox0))
        runs.extend(row_runs)
    res = (ox1 - ox0, oy1 - oy0, ox0, oy0, tuple(runs), adv * size / 512.0)
    _RASTER_CACHE[key] = res
    return res


class Img:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg)) * (w * h)

    def rect(self, x0, y0, x1, y1, color):
        x0 = max(0, int(x0))
        y0 = max(0, int(y0))
        x1 = min(self.w, int(x1))
        y1 = min(self.h, int(y1))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for y in range(y0, y1):
            o = (y * self.w + x0) * 3
            self.px[o:o + len(row)] = row

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            self.rect(x0, y + t, x1, y + t + 1, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            self.rect(x + t, y0, x + t + 1, y1, color)

    def line(self, x0, y0, x1, y1, color):
        x0 = int(x0)
        y0 = int(y0)
        x1 = int(x1)
        y1 = int(y1)
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            if 0 <= x < self.w and 0 <= y < self.h:
                o = (y * self.w + x) * 3
                self.px[o:o + 3] = bytes(color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def polyline(self, pts, color, close=False):
        n = len(pts)
        for k in range(n - 1):
            self.line(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1],
                      color)
        if close and n > 2:
            self.line(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1], color)

    def fill_poly(self, pts, color):
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0 = max(0, math.floor(min(ys)))
        y1 = min(self.h, math.ceil(max(ys)))
        row = None
        for (r, a, b) in _spans([pts], y0, y1):
            a = max(0, a)
            b = min(self.w, b)
            if b > a:
                o = (r * self.w + a) * 3
                self.px[o:o + 3 * (b - a)] = bytes(color) * (b - a)

    def circle(self, cx, cy, r, color):
        cx = int(cx)
        cy = int(cy)
        r = int(r)
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            y = cy + dy
            if 0 <= y < self.h:
                x0 = max(0, cx - dx)
                x1 = min(self.w, cx + dx + 1)
                if x1 > x0:
                    o = (y * self.w + x0) * 3
                    self.px[o:o + 3 * (x1 - x0)] = bytes(color) * (x1 - x0)

    def blit(self, mask, x, y, color):
        mw, mh, xoff, yoff, runs, _adv = mask
        cb = bytes(color)
        for (dy, a, b) in runs:
            yy = y + yoff + dy
            if yy < 0 or yy >= self.h:
                continue
            xx0 = x + xoff + a
            xx1 = x + xoff + b
            if xx1 <= 0 or xx0 >= self.w:
                continue
            c0 = max(0, xx0)
            c1 = min(self.w, xx1)
            if c1 > c0:
                o = (yy * self.w + c0) * 3
                self.px[o:o + 3 * (c1 - c0)] = cb * (c1 - c0)


def text_w(font, s, size, shear=0.0, bold=False):
    tot = 0.0
    for ch in s:
        tot += _glyph_adv(font, ch) * size / 512.0
    if bold:
        tot += max(0.6, size * 0.035) * len(s)
    return tot


def draw_text(img, font, s, x, y, size, color, shear=0.0, bold=False,
              align="left"):
    """Draw text with baseline at pixel row y. Returns width drawn."""
    w = text_w(font, s, size, shear, bold)
    if align == "center":
        x -= w / 2.0
    elif align == "right":
        x -= w
    pen = x
    for ch in s:
        if ch == " ":
            pen += _glyph_adv(font, " ") * size / 512.0
            continue
        m = rasterize(font, ch, size, shear, bold)
        img.blit(m, int(round(pen)), int(round(y)), color)
        pen += m[5]
    if bold:
        pen += max(0.6, size * 0.035) * len(s)
    return pen - x


def wrap(font, s, size, maxw, shear=0.0, bold=False):
    lines = []
    cur = ""
    for word in s.split(" "):
        t = (cur + " " + word).strip()
        if text_w(font, t, size, shear, bold) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(font, s, size, maxw, max_lines, min_size=6.0):
    """Reduce size until the text wraps to at most max_lines lines."""
    while size > min_size:
        lines = wrap(font, s, size, maxw)
        if len(lines) <= max_lines:
            return size, lines
        size -= 0.5
    return size, wrap(font, s, size, maxw)

# ---------------------------------------------------------------- data

TOP3 = [
    {
        "region": "MIDDLE EAST",
        "headline": "IRAN: MINES HIT TWO TANKERS",
        "summary": "Iran's Revolutionary Guards say two oil tankers were hit by "
                   "sea mines near Khasab at the Strait of Hormuz; Britain "
                   "reported a blast near a tanker west of Dubai. Oil prices jumped.",
        "source": "Reuters",
        "conf": "CLAIM",
    },
    {
        "region": "UNITED STATES",
        "headline": "STORM BATTERS EAST COAST",
        "summary": "A Thanksgiving nor'easter cuts power to about 900,000 "
                   "homes and businesses, stops Macy's parade for the first "
                   "time in 100 years and snarls holiday travel.",
        "source": "Reports",
        "conf": "REPORTED",
    },
    {
        "region": "MIDDLE EAST",
        "headline": "GAZA STRIKES ENTER THIRD NIGHT",
        "summary": "Israeli strikes kill nine in Gaza, including a "
                   "Hamas-appointed minister, on the third straight night; "
                   "Israel threatens to displace one million Palestinians "
                   "unless Hamas disarms.",
        "source": "Reuters",
        "conf": "REPORTED",
    },
]

MID = [
    ("ZELENSKYY WARNS OF MASS STRIKE",
     "President Zelenskyy warns Russia is preparing another massive "
     "strike on Ukraine's energy grid in the coming days.",
     "Reports", "CLAIM"),
    ("TRUMP DEMANDS GDP PROBE",
     "President Trump demands a probe into the GDP figures, calling "
     "the earlier data fake, after Q3 growth was revised to 4.3%.",
     "Reuters", "REPORTED"),
    ("TRUMP LASHES OUT AT FOES",
     "President Trump uses his Thanksgiving message to lash out at "
     "political foes, immigrants and the federal government.",
     "Reuters", "REPORTED"),
    ("TRUMP TO PUTIN: PULL BACK",
     "President Trump says he pressed Vladimir Putin to pull back all "
     "military aggression in Europe, in a social media post.",
     "Reuters", "REPORTED"),
    ("JAPAN PROTESTS US TARIFFS",
     "Japan protests the new US tariff rate and Washington's allegation "
     "of excess manufacturing capacity.",
     "Reports", "REPORTED"),
    ("SAUDI DOWNS MISSILES OVER RIYADH",
     "Saudi air defences destroy two Houthi ballistic missiles bound "
     "for Riyadh and drones over the Eastern Province.",
     "Reports", "REPORTED"),
    ("CONGO EBOLA CASES TOP 12,000",
     "A situation report published on Thursday puts Congo's confirmed "
     "Ebola cases at 12,021, with 5,904 deaths, as fighting hampers "
     "the response.",
     "Reports", "REPORTED"),
    ("UK MIGRATION FALLS TO 77,000",
     "Net migration to Britain falls to 77,000 in the year to June 2026, "
     "the lowest since 1997 outside the pandemic years.",
     "ONS", "OFFICIAL"),
    ("NVIDIA HALTS CHIP SHIPMENTS",
     "Nvidia halts advanced server shipments to four Southeast Asian "
     "countries amid US export controls.",
     "Reuters", "REPORTED"),
    ("RED-FLAG ORDER OVER WALZ PLOT",
     "Minnesota police obtain a red-flag order over an alleged "
     "plot against Governor Tim Walz.",
     "Reports", "REPORTED"),
]

# (place, fact, source) -- stories 14 to 40, one line each.
BRIEFS = [
    ("United States",
     "Trump says Putin can attend next month's G20 summit in Florida if he wants to come.",
     "Reports"),
    ("United States",
     "Trump tells US troops in Thanksgiving calls that victory over Iran is 'at hand'.",
     "Reports"),
    ("United States",
     "NFL Thanksgiving: Bears beat Lions 39-35.",
     "NFL"),
    ("United States",
     "New York Mayor Mamdani sends a Thanksgiving message, noting some tables will have less food this year.",
     "Reports"),
    ("Canada",
     "Alberta projects an $8.5 billion surplus for 2026-27 in its second-quarter update, on high oil prices.",
     "Reports"),
    ("Europe",
     "Britain invests £9.5m in a 200 MW wind farm in Ukraine, enough for about 300,000 homes.",
     "The Guardian"),
    ("Europe",
     "Macron sets a December deadline for a deal on the EU's next long-term budget.",
     "Reports"),
    ("Europe",
     "Germany arrests two Iraqi suspects over a plot to attack synagogues in Cologne and Heidelberg.",
     "Reports"),
    ("Europe",
     "Five European nations buy 430 CV90 combat vehicles.",
     "Reports"),
    ("Europe",
     "Spain's Pablo Hernandez de Cos picked as the new ECB chief.",
     "Reports"),
    ("Europe",
     "EU leaders debate a 45 billion euro loan for Ukraine at the Brussels summit; a decision is deferred to December.",
     "Reports"),
    ("Ukraine-Russia",
     "Ukraine's foreign minister expresses regret to Libya over weekend drone strikes that killed two naval officers off Benghazi.",
     "Reports"),
    ("Ukraine-Russia",
     "Ukraine says North Korea has temporarily halted some arms deliveries to Russia.",
     "Reports"),
    ("Ukraine-Russia",
     "Ukraine says it received 250 bodies in a swap with Russia.",
     "Reports"),
    ("Middle East",
     "Iranian drones intercepted over Kuwait; four injured, two Italian technicians reported killed.",
     "Reports"),
    ("Middle East",
     "Houthi media report Saudi airstrikes on Sanaa hours after the missile attack on Riyadh.",
     "Reports"),
    ("East Asia",
     "Bank of Korea raises rates to 3.25%.",
     "Bank of Korea"),
    ("East Asia",
     "China, Japan, South Korea and ASEAN launch talks on cross-border digital payments.",
     "Reports"),
    ("East Asia",
     "China reserves the right to take necessary measures after Trump's tariff proposals.",
     "The Guardian"),
    ("South Asia",
     "India's central bank clears the NSE to launch futures contracts on corporate bond indices.",
     "Reuters"),
    ("South Asia",
     "Bangladesh garment workers clash with police, a day after a wage deal.",
     "Reports"),
    ("South Asia",
     "World Chess Championship: Gukesh draws Game 3 vs Sindarov; match tied 1.5-1.5.",
     "Reports"),
    ("SE Asia & Pacific",
     "The Philippines asks the US for six Chinook helicopters under a $2 billion military financing package.",
     "Reports"),
    ("SE Asia & Pacific",
     "Bangkok refinery blast injures nine; residents told to evacuate.",
     "Reports"),
    ("SE Asia & Pacific",
     "UN experts demand Vietnam explain the 'abduction' of activists.",
     "Reports"),
    ("Africa",
     "Kenya court rules a US-backed Ebola quarantine site breached the constitution.",
     "Reuters"),
    ("Latin America",
     "WHO chief Tedros puts $1m into the last major public hospital still operating in Haiti's capital.",
     "Reports"),
]

REGIONS = [
    ("United States", 8, NAVY),
    ("Europe", 8, TEAL),
    ("Middle East", 5, RED),
    ("East Asia", 5, ORANGE),
    ("Ukraine-Russia", 4, PURPLE),
    ("South Asia", 3, GREEN),
    ("Southeast Asia and Pacific", 3, BLUE),
    ("Africa", 2, OCHRE),
    ("Canada", 1, SLATE),
    ("Latin America", 1, MAGENTA),
]

STRIP = [
    ("250", "BODIES RETURNED TO UKRAINE IN A SWAP"),
    ("900,000", "WITHOUT POWER IN THE THANKSGIVING STORM"),
    ("77,000", "UK NET MIGRATION, YEAR TO JUNE 2026"),
    ("3.25%", "BANK OF KOREA RAISES RATES TO 3.25%"),
    ("12,021", "EBOLA CASES IN CONGO IN THURSDAY'S REPORT"),
    ("1.5-1.5", "WORLD CHESS FINAL TIED AFTER GAME 3 DRAW"),
]

TIMELINE = [
    ("00:05 UTC",
     "Saudi defences destroy two Houthi ballistic missiles bound for Riyadh.",
     9),
    ("06:49 UTC",
     "Bank of Korea raises its policy rate to 3.25%.",
     30),
    ("10:00 UTC",
     "Japan's chief cabinet secretary protests the new US tariff rate.",
     8),
    ("12:00 UTC",
     "China reserves the right to necessary measures over US tariffs.",
     32),
    ("15:59 UTC",
     "Trump tells Putin to pull back all military aggression in Europe.",
     7),
    ("20:33 UTC",
     "Israeli strikes kill nine in Gaza on the third straight night.",
     3),
]

DATECHECK = [
    ("Mon 23 Nov", "Nvidia chief Jensen Huang returns as CEO."),
    ("Mon 23 Nov", "S&P 500 jumps 4.73%, Nikkei 3.91% on the Huang return."),
    ("Sun 22 Nov", "Ukrainian drones strike Benghazi port, Libya (admitted Thu 26 Nov)."),
    ("Tue 24 Nov", "First foreign astronaut joins China's Tiangong station."),
    ("Tue 24 Nov", "COP31 closes without agreement on fossil fuels."),
    ("Wed 25 Nov", "S&P 500 drops 0.25% in a 3.2% intraday plunge; $3.6T wiped at the lows."),
]

LEGEND = ("OFFICIAL = confirmed by an official source   -   REPORTED = "
          "reported by a news outlet   -   CLAIM = claimed by a party to "
          "the story   -   CONFIRMED = confirmed by two or more "
          "independent sources")

CONF_COLORS = {
    "OFFICIAL": NAVY,
    "REPORTED": RED,
    "CLAIM": GOLD,
    "CONFIRMED": TEAL,
}

# Simplified continent outlines as (lon, lat) points.
CONTINENTS = [
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-112, 68), (-100, 69),
     (-92, 66), (-85, 66), (-80, 73), (-76, 62), (-70, 58), (-65, 49),
     (-70, 43), (-75, 36), (-80, 32), (-81, 26), (-84, 30), (-89, 21),
     (-92, 15), (-86, 12), (-83, 9), (-90, 14), (-97, 16), (-104, 20),
     (-110, 23), (-114, 28), (-120, 34), (-124, 42), (-125, 49),
     (-130, 55), (-140, 60), (-150, 61), (-158, 58), (-165, 60)],
    [(-79, 9), (-76, 4), (-72, 0), (-68, -3), (-62, -6), (-55, -4),
     (-50, 0), (-44, -3), (-38, -6), (-35, -9), (-36, -15), (-39, -20),
     (-41, -27), (-48, -28), (-54, -34), (-58, -38), (-63, -41),
     (-66, -47), (-69, -52), (-71, -54), (-74, -50), (-73, -44),
     (-72, -36), (-71, -28), (-71, -19), (-76, -14), (-80, -8), (-81, -2)],
    [(-10, 37), (-8, 43), (-2, 44), (-4, 48), (-1, 51), (2, 51), (5, 53),
     (8, 57), (10, 59), (12, 55), (18, 56), (21, 55), (24, 59), (28, 59),
     (30, 60), (28, 62), (21, 64), (18, 69), (25, 71), (31, 70), (35, 67),
     (40, 64), (42, 60), (40, 56), (38, 52), (35, 48), (32, 45), (30, 46),
     (28, 44), (24, 42), (20, 42), (18, 40), (15, 38), (12, 42), (8, 44),
     (3, 43), (0, 40), (-2, 37)],
    [(-6, 35), (-10, 31), (-10, 27), (-13, 20), (-16, 15), (-17, 12),
     (-12, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (12, 0),
     (12, -5), (13, -10), (12, -17), (13, -22), (16, -28), (19, -34),
     (25, -34), (29, -29), (32, -26), (35, -20), (36, -15), (40, -11),
     (41, -4), (44, 2), (48, 7), (51, 11), (48, 12), (44, 13), (43, 12),
     (40, 15), (39, 20), (37, 25), (35, 28), (33, 31), (30, 32), (25, 32),
     (20, 32), (15, 32), (11, 34), (8, 37), (3, 37)],
    [(30, 36), (33, 36), (36, 36), (40, 38), (44, 39), (48, 40),
     (50, 44), (50, 48), (54, 51), (58, 52), (60, 55), (63, 58),
     (66, 61), (68, 65), (70, 68), (72, 71), (76, 72), (80, 73),
     (85, 74), (95, 76), (105, 77), (115, 73), (125, 72), (135, 71),
     (145, 72), (155, 70), (162, 66), (170, 66), (178, 65), (178, 62),
     (170, 60), (162, 56), (158, 52), (155, 51), (150, 59), (142, 59),
     (141, 52), (140, 44), (137, 38), (132, 35), (129, 33), (127, 35),
     (126, 38), (122, 39), (120, 34), (122, 30), (120, 26), (116, 22),
     (112, 21), (109, 18), (106, 10), (104, 8), (101, 6), (99, 9),
     (97, 12), (94, 16), (92, 21), (89, 22), (87, 20), (85, 19),
     (82, 16), (80, 13), (77, 8), (75, 10), (73, 16), (70, 20),
     (67, 23), (64, 25), (61, 25), (58, 26), (55, 26), (52, 28),
     (50, 29), (48, 30), (45, 29), (42, 28), (39, 27), (36, 30),
     (33, 31), (30, 36)],
    [(113, -22), (114, -28), (115, -33), (119, -34), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (147, -39), (150, -37), (150, -34), (150, -28),
     (148, -22), (146, -19), (143, -15), (141, -13), (137, -12),
     (134, -12), (131, -12), (128, -14), (124, -15), (120, -14),
     (116, -16), (114, -20)],
]

# (lon, lat, story number, label dx, label dy) in map pixels.
MAP_PINS = [
    (56.5, 26.2, 1, 6, -6),
    (-74.5, 40.5, 2, -2, -8),
    (34.5, 31.5, 3, 8, -8),
    (30.5, 50.4, 4, -6, -10),
    (-77.0, 38.9, 5, 14, -6),
    (-80.0, 26.7, 6, 0, -8),
    (-80.1, 26.8, 7, -14, 10),
    (138.5, 37.5, 8, 0, -8),
    (50.1, 26.6, 9, 10, 10),
    (23.5, -1.5, 10, -12, 12),
    (-0.1, 51.5, 11, 0, -8),
    (103.8, 1.35, 12, 0, 8),
    (-93.1, 45.0, 13, -10, -8),
]

# ---------------------------------------------------------------- layout

MX = 14          # side margin
CW = W - 2 * MX  # content width = 996


def badge(img, x, y, label, color, size=8.0):
    """Small rounded-ish confidence badge; returns its width."""
    w = text_w(SANS_FONT, label, size, bold=True) + 10
    h = size + 6
    img.rect(x, y, x + w, y + h, color)
    draw_text(img, SANS_FONT, label, x + 5, y + h - 4.5, size, WHITE,
              bold=True)
    return w


def draw_top(img):
    # Navy top band.
    img.rect(0, 0, W, 26, NAVY)
    draw_text(img, SANS_FONT,
              "40 STORIES  -  10 REGIONS  -  THURSDAY 26 NOVEMBER 2026  "
              "-  THE WORLD IN ONE PAGE",
              W / 2, 18, 12.5, WHITE, bold=True, align="center")
    # Giant serif date line.
    size = 50.0
    while text_w(SERIFB_FONT, "THURSDAY 26 NOVEMBER 2026", size) > CW \
            and size > 20:
        size -= 1
    draw_text(img, SERIFB_FONT, "THURSDAY 26 NOVEMBER 2026",
              W / 2, 72, size, NAVY, bold=True, align="center")
    img.hline(MX, W - MX, 80, RED, 2)


def draw_headlines(img):
    y = 106
    for i, story in enumerate(TOP3, start=1):
        draw_text(img, SERIFB_FONT, "%d. %s" % (i, story["headline"]),
                  W / 2, y, 26, RED, shear=0.16, bold=True, align="center")
        y += 29
    img.hline(MX, W - MX, 170, NAVY, 1)


def draw_strip(img):
    y0 = 174
    bw = 162
    gap = 5
    x = MX
    for number, label in STRIP:
        img.rect(x, y0, x + bw, y0 + 60, NAVY)
        img.rect(x + 1, y0 + 1, x + bw - 1, y0 + 59, WHITE)
        img.hline(x, x + bw, y0, RED, 3)
        draw_text(img, SERIFB_FONT, number, x + bw / 2, y0 + 32, 27, RED,
                  bold=True, align="center")
        lines = wrap(SANS_FONT, label, 8.5, bw - 10, bold=True)
        ly = y0 + 44
        for ln in lines[:2]:
            draw_text(img, SANS_FONT, ln, x + bw / 2, ly, 8.5, NAVY,
                      bold=True, align="center")
            ly += 10
        x += bw + gap


def draw_pills(img):
    rows = [REGIONS[:5], REGIONS[5:]]
    y = 238
    for row in rows:
        pw = (CW - 4 * 6) / 5.0
        x = MX
        for name, count, color in row:
            img.rect(x, y, x + pw, y + 18, color)
            draw_text(img, SANS_FONT, "%s  %d" % (name, count),
                      x + pw / 2, y + 13.5, 10.5, WHITE, bold=True,
                      align="center")
            x += pw + 6
        y += 20


def draw_big_cards(img):
    y0 = 280
    h = 132
    cw = (CW - 2 * 10) / 3.0
    x = MX
    for i, story in enumerate(TOP3, start=1):
        img.rect(x, y0, x + cw, y0 + h, CARD)
        img.rect(x, y0, x + cw, y0 + 3, RED)
        # number disc
        img.circle(x + 18, y0 + 20, 11, RED)
        draw_text(img, SANS_FONT, str(i), x + 18, y0 + 24, 12, WHITE,
                  bold=True, align="center")
        draw_text(img, SANS_FONT, story["region"], x + 34, y0 + 24, 10,
                  RED, bold=True)
        size, lines = fit_lines(SERIFB_FONT, story["headline"], 17,
                                 cw - 16, 2)
        ly = y0 + 44
        for ln in lines:
            draw_text(img, SERIFB_FONT, ln, x + 8, ly, size, NAVY,
                      bold=True)
            ly += size + 3
        size2, lines2 = fit_lines(SANS_FONT, story["summary"], 9.5,
                                   cw - 16, 4)
        ly += 2
        for ln in lines2:
            draw_text(img, SANS_FONT, ln, x + 8, ly, size2, NAVY)
            ly += size2 + 2.5
        draw_text(img, SANS_FONT, "Source: " + story["source"],
                  x + 8, y0 + h - 8, 8.5, GREY, shear=0.12)
        bw = text_w(SANS_FONT, story["conf"], 8.0, bold=True) + 10
        badge(img, x + cw - 8 - bw, y0 + h - 20, story["conf"],
              CONF_COLORS[story["conf"]], 8.0)
        x += cw + 10


def draw_mid_grid(img):
    y0 = 416
    rh = 85
    cw = (CW - 4 * 8) / 5.0
    for row in range(2):
        y = y0 + row * (rh + 4)
        x = MX
        for col in range(5):
            idx = row * 5 + col
            headline, summary, source, conf = MID[idx]
            num = idx + 4
            img.rect(x, y, x + cw, y + rh, CARD)
            img.rect(x, y, x + cw, y + 2, NAVY)
            img.circle(x + 12, y + 13, 8, RED)
            draw_text(img, SANS_FONT, str(num), x + 12, y + 16, 9, WHITE,
                      bold=True, align="center")
            size, lines = fit_lines(SERIFB_FONT, headline, 11.5, cw - 26,
                                     2)
            ly = y + 17
            for ln in lines[:1]:
                draw_text(img, SERIFB_FONT, ln, x + 24, ly, size, NAVY,
                          bold=True)
                ly += size + 2
            if len(lines) > 1:
                draw_text(img, SERIFB_FONT, lines[1], x + 8, ly, size,
                          NAVY, bold=True)
                ly += size + 2
            size2, lines2 = fit_lines(SANS_FONT, summary, 8, cw - 16, 3)
            for ln in lines2:
                draw_text(img, SANS_FONT, ln, x + 8, ly, size2, NAVY)
                ly += size2 + 1.5
            draw_text(img, SANS_FONT, source, x + 8, y + rh - 7, 7.5,
                      GREY, shear=0.12)
            bw = text_w(SANS_FONT, conf, 7.0, bold=True) + 10
            badge(img, x + cw - 8 - bw, y + rh - 17, conf,
                  CONF_COLORS[conf], 7.0)
            x += cw + 8


def draw_timeline(img):
    y0 = 594
    img.rect(MX, y0, W - MX, y0 + 52, WHITE)
    img.rect(MX, y0, W - MX, y0 + 2, RED)
    colw = CW / 6.0
    for i, (t, text, num) in enumerate(TIMELINE):
        x = MX + i * colw + 6
        w = colw - 12
        draw_text(img, SANS_FONT, t, x, y0 + 15, 10, RED, bold=True)
        if num is not None:
            draw_text(img, SANS_FONT, "#%d" % num, x + w, y0 + 15, 9,
                      NAVY, bold=True, align="right")
        lines = wrap(SANS_FONT, text, 8, w)
        ly = y0 + 27
        for ln in lines[:3]:
            draw_text(img, SANS_FONT, ln, x, ly, 8, NAVY)
            ly += 9.5


def _project(lon, lat, x0, y0, w, h):
    px = x0 + (lon + 170.0) / 360.0 * w
    py = y0 + (75.0 - lat) / 130.0 * h
    return (px, py)


def draw_map(img):
    y0 = 650
    img.rect(MX, y0, W - MX, y0 + 90, (238, 244, 248))
    draw_text(img, SANS_FONT, "WORLD MAP - STORY LOCATIONS 1 TO 13",
              MX + 2, y0 + 11, 9.5, NAVY, bold=True)
    mx0, my0, mw, mh = MX + 4, y0 + 15, CW - 8, 72
    for cont in CONTINENTS:
        pts = [(int(round(_project(lon, lat, mx0, my0, mw, mh)[0])),
                int(round(_project(lon, lat, mx0, my0, mw, mh)[1])))
               for (lon, lat) in cont]
        img.fill_poly(pts, LAND)
        img.polyline(pts, LAND_LN, close=True)
    for (lon, lat, num, dx, dy) in MAP_PINS:
        bx, by = _project(lon, lat, mx0, my0, mw, mh)
        lx, ly = int(round(bx)) + dx, int(round(by)) + dy
        img.line(int(round(bx)), int(round(by)), lx, ly, RED)
        img.circle(int(round(bx)), int(round(by)), 2, NAVY)
        img.circle(lx, ly, 8, WHITE)
        img.circle(lx, ly, 7, RED)
        draw_text(img, SANS_FONT, str(num), lx, ly + 3, 8.5, WHITE,
                  bold=True, align="center")


def _fit_brief_size(place, fact, source, num, maxw):
    size = 9.0
    while size > 7.0:
        w = text_w(SANS_FONT, "%d. " % num, size, bold=True)
        w += text_w(SANS_FONT, place + ": ", size, bold=True)
        w += text_w(SANS_FONT, fact + "  ", size)
        w += text_w(SANS_FONT, "- " + source, size)
        if w <= maxw:
            return size
        size -= 0.5
    return size


def draw_briefs(img):
    draw_text(img, SANS_FONT, "THE REST OF THE DAY - STORIES 14 TO 40",
              MX, 752, 10.5, NAVY, bold=True)
    img.hline(MX, W - MX, 756, NAVY, 1)
    colw = (CW - 16) / 2.0
    for row in range(14):
        y = 768 + row * 12
        for col in range(2):
            idx = row + col * 14
            if idx >= len(BRIEFS):
                continue
            num = idx + 14
            place, fact, source = BRIEFS[idx]
            x = MX + col * (colw + 16)
            size = _fit_brief_size(place, fact, source, num, colw)
            pen = x
            pen += draw_text(img, SANS_FONT, "%d. " % num, pen, y, size,
                             RED, bold=True)
            pen += draw_text(img, SANS_FONT, place + ": ", pen, y, size,
                             NAVY, bold=True)
            pen += draw_text(img, SANS_FONT, fact + "  ", pen, y, size,
                             NAVY)
            draw_text(img, SANS_FONT, "- " + source, pen, y, size, GREY,
                      shear=0.12)


def draw_datecheck(img):
    y0 = 924
    img.rect(MX, y0, W - MX, y0 + 98, WHITE)
    # red frame
    img.rect(MX, y0, W - MX, y0 + 2, RED)
    img.rect(MX, y0 + 96, W - MX, y0 + 98, RED)
    img.rect(MX, y0, MX + 2, y0 + 98, RED)
    img.rect(W - MX - 2, y0, W - MX, y0 + 98, RED)
    draw_text(img, SANS_FONT,
              "DATE CHECK - THESE HAPPENED ON OTHER DAYS, NOT 26 NOVEMBER",
              MX + 8, y0 + 15, 11.5, RED, bold=True)
    colw = (CW - 16) / 2.0
    for row in range(3):
        y = y0 + 29 + row * 13
        for col in range(2):
            idx = row + col * 3
            day, text = DATECHECK[idx]
            x = MX + 8 + col * (colw + 8)
            draw_text(img, SANS_FONT, day + " - ", x, y, 8.5, RED,
                      bold=True)
            wday = text_w(SANS_FONT, day + " - ", 8.5, bold=True)
            draw_text(img, SANS_FONT, text, x + wday, y, 8.5, NAVY)
    lines = wrap(SANS_FONT, LEGEND, 8, CW - 16)
    ly = y0 + 74
    for ln in lines[:2]:
        draw_text(img, SANS_FONT, ln, MX + 8, ly, 8, NAVY)
        ly += 10


def draw_page():
    global SERIFB_FONT, SANS_FONT
    SERIFB_FONT = _decode_font(SERIFB)
    SANS_FONT = _decode_font(SANS)
    img = Img(W, H, CREAM)
    draw_top(img)
    draw_headlines(img)
    draw_strip(img)
    draw_pills(img)
    draw_big_cards(img)
    draw_mid_grid(img)
    draw_timeline(img)
    draw_map(img)
    draw_briefs(img)
    draw_datecheck(img)
    return img

# ---------------------------------------------------------------- output


def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(img, path):
    raw = bytearray()
    w, h = img.w, img.h
    for y in range(h):
        raw.append(0)
        raw += img.px[y * w * 3:(y + 1) * w * 3]
    comp = zlib.compress(bytes(raw), 6)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", comp)
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    # Output directory is resolved first, and entry.png is written
    # only there. Nothing is ever written into the program's own folder.
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    img = draw_page()
    write_png(img, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()

# GLYPH NOTE
# The CHARSET / SERIFB / SANS strings above hold glyph outline data
# extracted on the build machine with a throwaway helper script
# (/tmp/extract_glyphs.py, using fontTools) from two fonts already
# installed on this machine:
#   - DejaVuSerif-Bold.ttf (/usr/share/fonts/truetype/dejavu/)
#     for the serif display face (date line, headlines, card headlines)
#   - DejaVuSans.ttf (/usr/share/fonts/truetype/dejavu/)
#     for the sans face (labels, summaries, briefs, small text)
# For each of 95 characters (ASCII 32-126 plus em dash, en dash, right
# single quote, curly double quotes, bullet, multiplication sign and
# ellipsis) the helper flattened every quadratic curve of the glyph
# outline into line segments (tolerance 10 font units), quantised the
# coordinates to a 512-units-per-em grid, and packed the advance width
# and contour point deltas as compact base-64 varints. No font file is
# read at run time and no third-party package is imported.
